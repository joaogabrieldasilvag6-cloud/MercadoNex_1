from django.shortcuts import render
from .models import Venda, ItemVenda
from apps.clientes.models import Cliente
from apps.produtos.models import Produto

import json
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def vendas(request):
    clientes = Cliente.objects.all().order_by("nome")
    produtos = Produto.objects.filter(status=True).order_by("nome")
    categorias = list(
        Produto.objects.filter(status=True)
        .exclude(categoria="")
        .values_list("categoria", flat=True)
        .distinct()
        .order_by("categoria")
    )

    hoje = timezone.localdate()
    vendas_hoje = Venda.objects.filter(status="FINALIZADA", data__date=hoje)
    faturamento_hoje = vendas_hoje.aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    itens_hoje = ItemVenda.objects.filter(venda__in=vendas_hoje).aggregate(total=Sum("quantidade"))["total"] or 0

    emojis = {
        "bebidas": "🥤", "mercearia": "🛒", "padaria": "🥖", "higiene": "🧴",
        "limpeza": "🧹", "frios": "🧀", "laticínios": "🥛", "laticinios": "🥛",
        "carnes": "🥩", "hortifruti": "🥬", "frutas": "🍎", "verduras": "🥬",
        "doces": "🍫", "congelados": "🧊", "pet": "🐾", "outros": "📦",
    }
    for produto in produtos:
        produto.emoji = emojis.get(produto.categoria.strip().lower(), "🛒")

    return render(request, "privado/vendas.html", {
        "clientes": clientes,
        "produtos": produtos,
        "categorias": categorias,
        "faturamento_hoje": faturamento_hoje,
        "vendas_hoje": vendas_hoje.count(),
        "itens_hoje": itens_hoje,
    })


@login_required
@require_POST
@transaction.atomic
def finalizar_venda(request):
    try:
        dados = json.loads(request.body or "{}")
        itens_recebidos = dados.get("itens") or []
        forma_pagamento = str(dados.get("forma_pagamento") or "").upper()
        cliente_id = dados.get("cliente")

        formas_validas = {"PIX", "DEBITO", "CREDITO", "DINHEIRO", "FIADO"}
        if forma_pagamento not in formas_validas:
            return JsonResponse({"sucesso": False, "erro": "Forma de pagamento inválida."}, status=400)
        if not itens_recebidos:
            return JsonResponse({"sucesso": False, "erro": "O carrinho está vazio."}, status=400)

        try:
            desconto_percentual = Decimal(str(dados.get("desconto_percentual", 0)))
        except (InvalidOperation, TypeError):
            return JsonResponse({"sucesso": False, "erro": "Desconto inválido."}, status=400)
        if not 0 <= desconto_percentual <= 100:
            return JsonResponse({"sucesso": False, "erro": "O desconto deve estar entre 0% e 100%."}, status=400)

        cliente = None
        if cliente_id not in (None, "", 0, "0"):
            cliente = get_object_or_404(Cliente.objects.select_for_update(), pk=cliente_id)

        # Fiado exige cliente e usa o limite/saldo cadastrados no cliente.
        if forma_pagamento == "FIADO":
            if cliente is None:
                return JsonResponse({"sucesso": False, "erro": "Para vender fiado, selecione um cliente."}, status=400)
            if not cliente.ativo_fiado:
                return JsonResponse({"sucesso": False, "erro": "O fiado deste cliente está desativado."}, status=400)

        itens_normalizados = {}
        for item in itens_recebidos:
            try:
                produto_id = int(item.get("id"))
                quantidade = int(item.get("quantidade"))
            except (TypeError, ValueError, AttributeError):
                return JsonResponse({"sucesso": False, "erro": "Item de venda inválido."}, status=400)
            if quantidade <= 0:
                return JsonResponse({"sucesso": False, "erro": "A quantidade deve ser maior que zero."}, status=400)
            itens_normalizados[produto_id] = itens_normalizados.get(produto_id, 0) + quantidade

        produtos_bloqueados = {}
        subtotal = Decimal("0.00")
        for produto_id, quantidade in itens_normalizados.items():
            produto = Produto.objects.select_for_update().filter(pk=produto_id, status=True).first()
            if not produto:
                return JsonResponse({"sucesso": False, "erro": f"Produto #{produto_id} não está disponível."}, status=400)
            if quantidade > produto.quantidade:
                return JsonResponse({"sucesso": False, "erro": f"Estoque insuficiente para {produto.nome}. Disponível: {produto.quantidade}."}, status=400)
            preco = Decimal(produto.preco_venda)
            subtotal += preco * quantidade
            produtos_bloqueados[produto_id] = produto

        desconto_valor = (subtotal * desconto_percentual / Decimal("100")).quantize(Decimal("0.01"))
        valor_final = (subtotal - desconto_valor).quantize(Decimal("0.01"))

        valor_recebido = None
        if forma_pagamento == "DINHEIRO":
            try:
                valor_recebido = Decimal(str(dados.get("valor_recebido", 0)))
            except (InvalidOperation, TypeError):
                return JsonResponse({"sucesso": False, "erro": "Valor recebido inválido."}, status=400)
            if valor_recebido < valor_final:
                return JsonResponse({"sucesso": False, "erro": "O valor recebido é menor que o total da venda."}, status=400)

        # Verificação do limite de crédito do fiado antes de gravar a venda.
        novo_saldo_fiado = None
        if forma_pagamento == "FIADO":
            saldo_atual = Decimal(cliente.saldo_fiado or 0)
            limite = Decimal(cliente.limite_fiado or 0)
            novo_saldo_fiado = (saldo_atual + valor_final).quantize(Decimal("0.01"))
            if novo_saldo_fiado > limite:
                disponivel = max(Decimal("0.00"), limite - saldo_atual).quantize(Decimal("0.01"))
                return JsonResponse({
                    "sucesso": False,
                    "erro": f"Limite de fiado excedido. Saldo atual: R$ {saldo_atual:.2f}. Disponível: R$ {disponivel:.2f}.",
                }, status=400)

        venda = Venda.objects.create(
            cliente=cliente,
            status="FINALIZADA",
            forma_pagamento=forma_pagamento,
            total=subtotal.quantize(Decimal("0.01")),
            desconto=desconto_valor,
            valor_final=valor_final,
        )

        for produto_id, quantidade in itens_normalizados.items():
            produto = produtos_bloqueados[produto_id]
            preco = Decimal(produto.preco_venda)
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco,
                subtotal=(preco * quantidade).quantize(Decimal("0.01")),
            )
            produto.quantidade -= quantidade
            produto.save(update_fields=["quantidade", "data_atualizacao"])

        # A dívida do cliente é atualizada somente depois que a venda e os itens foram criados.
        if forma_pagamento == "FIADO":
            cliente.saldo_fiado = novo_saldo_fiado
            cliente.save(update_fields=["saldo_fiado"])

        resposta = {
            "sucesso": True,
            "venda_id": venda.id,
            "total": str(venda.total),
            "desconto": str(venda.desconto),
            "valor_final": str(venda.valor_final),
            "forma_pagamento": forma_pagamento,
        }
        if valor_recebido is not None:
            resposta["valor_recebido"] = str(valor_recebido.quantize(Decimal("0.01")))
            resposta["troco"] = str((valor_recebido - valor_final).quantize(Decimal("0.01")))
        if forma_pagamento == "FIADO":
            resposta["saldo_fiado_anterior"] = str(Decimal(cliente.saldo_fiado) - valor_final)
            resposta["novo_saldo_fiado"] = str(cliente.saldo_fiado)
            resposta["limite_fiado"] = str(cliente.limite_fiado)
        return JsonResponse(resposta)

    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "erro": "Dados da venda inválidos."}, status=400)
    except Exception as erro:
        return JsonResponse({"sucesso": False, "erro": str(erro)}, status=400)


