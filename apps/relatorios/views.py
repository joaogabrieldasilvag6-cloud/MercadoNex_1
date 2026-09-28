from django.shortcuts import render
import csv
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models.functions import TruncDate

from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from apps.vendas.models import ItemVenda, Venda


def _periodo(request):
    hoje = timezone.localdate()
    periodo = request.GET.get("periodo", "30")

    if periodo == "hoje":
        inicio = fim = hoje
    elif periodo == "7":
        inicio = hoje - timedelta(days=6)
        fim = hoje
    elif periodo == "mes":
        inicio = hoje.replace(day=1)
        fim = hoje
    elif periodo == "custom":
        try:
            inicio = timezone.datetime.fromisoformat(request.GET.get("inicio", "")).date()
            fim = timezone.datetime.fromisoformat(request.GET.get("fim", "")).date()
            if inicio > fim:
                inicio, fim = fim, inicio
        except (TypeError, ValueError):
            inicio = hoje - timedelta(days=29)
            fim = hoje
            periodo = "30"
    else:
        periodo = "30"
        inicio = hoje - timedelta(days=29)
        fim = hoje

    return periodo, inicio, fim


def _periodo_formatado(data):
    return data.strftime("%d/%m/%Y")


def _vendas_base(inicio, fim):
    return Venda.objects.filter(
        status="FINALIZADA",
        data__date__range=(inicio, fim),
    )


@login_required
def relatorios(request):
    periodo, inicio, fim = _periodo(request)
    vendas = _vendas_base(inicio, fim)

    faturamento = vendas.aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    quantidade_vendas = vendas.count()
    ticket_medio = faturamento / quantidade_vendas if quantidade_vendas else Decimal("0.00")
    descontos = vendas.aggregate(total=Sum("desconto"))["total"] or Decimal("0.00")
    unidades_vendidas = ItemVenda.objects.filter(venda__in=vendas).aggregate(total=Sum("quantidade"))["total"] or 0

    total_fiado = Cliente.objects.aggregate(total=Sum("saldo_fiado"))["total"] or Decimal("0.00")
    clientes_fiado = Cliente.objects.filter(saldo_fiado__gt=0).count()

    hoje = timezone.localdate()
    clientes_inadimplentes = Cliente.objects.filter(
        vendas__forma_pagamento="FIADO",
        vendas__status="FINALIZADA",
        vendas__fiado_pago=False,
        vendas__vencimento_fiado__lt=hoje,
    ).distinct().count()

    clientes_total = Cliente.objects.count()
    novos_clientes = Cliente.objects.filter(data_cadastro__date__range=(inicio, fim)).count()

    produtos_ativos_qs = Produto.objects.filter(status=True)
    produtos_ativos = produtos_ativos_qs.count()
    estoque_zerado = produtos_ativos_qs.filter(quantidade=0).count()
    estoque_baixo = produtos_ativos_qs.filter(quantidade__gt=0, quantidade__lte=10).count()

    vendidos_por_produto = {
        item["produto_id"]: item["unidades"] or 0
        for item in ItemVenda.objects.filter(venda__in=vendas)
        .values("produto_id")
        .annotate(unidades=Sum("quantidade"))
    }
    baixo_giro = sum(1 for produto in produtos_ativos_qs.only("id") if vendidos_por_produto.get(produto.id, 0) == 0)

    pagamentos_nomes = {
        "PIX": ("PIX", "pix"),
        "DEBITO": ("Débito", "debito"),
        "CREDITO": ("Crédito", "credito"),
        "DINHEIRO": ("Dinheiro", "dinheiro"),
        "FIADO": ("Fiado", "fiado"),
        "CARTAO": ("Cartão", "credito"),
    }
    pagamentos_brutos = vendas.values("forma_pagamento").annotate(valor=Sum("valor_final")).order_by()
    pagamentos = []
    for item in pagamentos_brutos:
        chave = item["forma_pagamento"] or "OUTRO"
        nome, classe = pagamentos_nomes.get(chave, (chave.title(), "debito"))
        valor = item["valor"] or Decimal("0.00")
        percentual = (valor / faturamento * 100) if faturamento else Decimal("0")
        pagamentos.append({
            "nome": nome,
            "classe": classe,
            "valor": valor,
            "percentual": percentual,
        })

    dias_qs = vendas.annotate(dia=TruncDate("data")).values("dia").annotate(valor=Sum("valor_final")).order_by("dia")
    por_data = {item["dia"]: item["valor"] or Decimal("0.00") for item in dias_qs}
    janela = (fim - inicio).days + 1
    datas_grafico = [inicio + timedelta(days=i) for i in range(min(janela, 31))]
    if janela > 31:
        # Em períodos maiores, mostra o último mês dentro do período para manter o gráfico legível.
        datas_grafico = [fim - timedelta(days=30 - i) for i in range(31)]

    maior_valor = max([por_data.get(data, Decimal("0.00")) for data in datas_grafico] or [Decimal("0.00")])
    vendas_por_dia = []
    for data in datas_grafico:
        valor = por_data.get(data, Decimal("0.00"))
        percentual = float((valor / maior_valor * 100) if maior_valor else 0)
        vendas_por_dia.append({
            "valor": valor,
            "percentual": max(3, round(percentual, 2)) if valor else 2,
            "dia_semana": data.strftime("%a").capitalize().replace("Thu", "Qui").replace("Wed", "Qua").replace("Tue", "Ter").replace("Mon", "Seg").replace("Fri", "Sex").replace("Sat", "Sáb").replace("Sun", "Dom"),
            "rotulo_curto": data.strftime("%d/%m"),
            "rotulo": data.strftime("%d/%m/%Y"),
        })

    if datas_grafico:
        maior_data = max(datas_grafico, key=lambda data: por_data.get(data, Decimal("0.00")))
        maior_dia = {
            "valor": por_data.get(maior_data, Decimal("0.00")),
            "rotulo": maior_data.strftime("%d/%m/%Y"),
        }
    else:
        maior_dia = {"valor": Decimal("0.00"), "rotulo": "-"}

    produtos_mais_vendidos = list(
        ItemVenda.objects.filter(venda__in=vendas)
        .values("produto__nome", "produto__categoria")
        .annotate(unidades=Sum("quantidade"), faturamento=Sum("subtotal"))
        .order_by("-unidades", "-faturamento")[:8]
    )
    for item in produtos_mais_vendidos:
        item["nome"] = item.pop("produto__nome")
        item["categoria"] = item.pop("produto__categoria")

    contexto = {
        "periodo": periodo,
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "inicio_formatado": _periodo_formatado(inicio),
        "fim_formatado": _periodo_formatado(fim),
        "faturamento": faturamento,
        "quantidade_vendas": quantidade_vendas,
        "ticket_medio": ticket_medio,
        "descontos": descontos,
        "unidades_vendidas": unidades_vendidas,
        "total_fiado": total_fiado,
        "clientes_fiado": clientes_fiado,
        "clientes_inadimplentes": clientes_inadimplentes,
        "clientes_total": clientes_total,
        "novos_clientes": novos_clientes,
        "produtos_ativos": produtos_ativos,
        "estoque_zerado": estoque_zerado,
        "estoque_baixo": estoque_baixo,
        "baixo_giro": baixo_giro,
        "pagamentos": pagamentos,
        "vendas_por_dia": vendas_por_dia,
        "maior_dia": maior_dia,
        "produtos_mais_vendidos": produtos_mais_vendidos,
    }

    return render(request, "privado/relatorios.html", contexto)


def _csv_response(nome, cabecalho, linhas):
    resposta = HttpResponse(content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = f'attachment; filename="{nome}"'
    resposta.write("\\ufeff")
    escritor = csv.writer(resposta, delimiter=";")
    escritor.writerow(cabecalho)
    escritor.writerows(linhas)
    return resposta


@login_required
def relatorios_exportar_vendas(request):
    periodo, inicio, fim = _periodo(request)
    vendas = _vendas_base(inicio, fim).select_related("cliente")
    linhas = []
    for venda in vendas.order_by("data"):
        itens = venda.itens.aggregate(total=Sum("quantidade"))["total"] or 0
        linhas.append([
            venda.id,
            venda.data.strftime("%d/%m/%Y %H:%M"),
            venda.cliente.nome if venda.cliente else "Consumidor Final",
            itens,
            venda.forma_pagamento,
            f"{venda.valor_final:.2f}",
            f"{venda.desconto:.2f}",
        ])
    return _csv_response(
        f"vendas_{inicio.isoformat()}_{fim.isoformat()}.csv",
        ["Venda", "Data", "Cliente", "Itens", "Pagamento", "Valor final", "Desconto"],
        linhas,
    )


@login_required
def relatorios_exportar_produtos(request):
    _, inicio, fim = _periodo(request)
    vendas = _vendas_base(inicio, fim)
    produtos = ItemVenda.objects.filter(venda__in=vendas).values("produto__nome", "produto__categoria").annotate(
        unidades=Sum("quantidade"), faturamento=Sum("subtotal")
    ).order_by("-unidades", "-faturamento")
    linhas = [
        [p["produto__nome"], p["produto__categoria"], p["unidades"], f"{p['faturamento'] or 0:.2f}"]
        for p in produtos
    ]
    return _csv_response(
        f"produtos_mais_vendidos_{inicio.isoformat()}_{fim.isoformat()}.csv",
        ["Produto", "Categoria", "Unidades", "Faturamento"],
        linhas,
    )


@login_required
def relatorios_exportar_estoque(request):
    produtos = Produto.objects.all().order_by("nome")
    linhas = [
        [p.nome, p.codigo, p.categoria, p.quantidade, f"{p.preco_venda:.2f}", "Ativo" if p.status else "Inativo"]
        for p in produtos
    ]
    return _csv_response(
        f"estoque_{timezone.localdate().isoformat()}.csv",
        ["Produto", "Código", "Categoria", "Quantidade", "Preço de venda", "Status"],
        linhas,
    )


@login_required
def relatorios_exportar_clientes(request):
    clientes = Cliente.objects.all().order_by("nome")
    linhas = [
        [p.nome, p.cpf, p.telefone, p.email or "", f"{p.saldo_fiado:.2f}", f"{p.limite_fiado:.2f}", "Ativo" if p.ativo_fiado else "Bloqueado"]
        for p in clientes
    ]
    return _csv_response(
        f"clientes_fiado_{timezone.localdate().isoformat()}.csv",
        ["Nome", "CPF", "Telefone", "E-mail", "Saldo fiado", "Limite fiado", "Status"],
        linhas,
    )
