import csv
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.produtos.models import Produto, Estoque
from .models import MovimentacaoEstoque

try:
    from apps.core.models import Mercadinho
except ImportError:
    Mercadinho = None


def _decimal(value, default=Decimal("0")):
    if value in (None, ""):
        return default
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        return default


def _attr(obj, *names, default=None):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def _latest_stock(produto):
    return Estoque.objects.filter(produto=produto).order_by("-data_entrada", "-id").first()


def _normalize(produto):
    lote = _latest_stock(produto)
    quantidade = int(getattr(produto, "quantidade", 0) or 0)
    categoria = str(getattr(produto, "categoria", "Sem categoria") or "Sem categoria")
    codigo = str(_attr(produto, "codigo", "codigo_barras", "ean", default="") or "")
    unidade = str(_attr(produto, "unidade", default="UN") or "UN")

    # O modelo Produto atual não possui um estoque mínimo no código já existente.
    # Mantemos 10 como padrão e, caso o campo exista futuramente, ele passa a ser usado.
    minimo = int(_attr(produto, "estoque_minimo", "quantidade_minima", default=10) or 10)
    if lote is not None:
        minimo = int(_attr(lote, "estoque_minimo", "quantidade_minima", default=minimo) or minimo)

    custo = _decimal(_attr(produto, "preco_custo", "custo_unitario", "custo", default=0))
    validade = lote.validade if lote else None
    dias_validade = (validade - date.today()).days if validade else None

    if quantidade <= 0:
        status = "falta"
        status_label = "Em falta"
    elif dias_validade is not None and 0 <= dias_validade <= 7:
        status = "vencendo"
        status_label = "Vencendo"
    elif quantidade <= minimo:
        status = "baixo"
        status_label = "Estoque baixo"
    else:
        status = "regular"
        status_label = "Regular"

    capacidade = max(minimo * 2, quantidade, 1)
    percentual = min(100, max(0, round((quantidade / capacidade) * 100, 1)))

    imagem_url = ""
    imagem = _attr(produto, "imagem", default=None)
    try:
        if imagem:
            imagem_url = imagem.url
    except Exception:
        pass

    return {
        "produto_id": produto.pk,
        "nome": produto.nome,
        "codigo": codigo,
        "categoria": categoria,
        "quantidade": quantidade,
        "minimo": minimo,
        "unidade": unidade,
        "custo": custo,
        "validade": validade.strftime("%d/%m/%Y") if validade else "",
        "validade_iso": validade.isoformat() if validade else "",
        "dias_validade": dias_validade,
        "status": status,
        "status_label": status_label,
        "percentual": percentual,
        "imagem": imagem_url,
        "lote": lote.pk if lote else "",
    }


def _save_quantity(produto, quantidade):
    produto.quantidade = int(quantidade)
    produto.save(update_fields=["quantidade"])


def _registrar_movimento(request, produto, tipo, quantidade, anterior, novo, observacao=""):
    return MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=int(quantidade),
        estoque_anterior=int(anterior),
        estoque_novo=int(novo),
        usuario=request.user if getattr(request.user, "is_authenticated", False) else None,
        observacao=observacao or "",
    )


@login_required
def estoque(request):
    produtos = Produto.objects.all().order_by("nome")
    itens = [_normalize(produto) for produto in produtos]

    categorias = sorted(
        {item["categoria"] for item in itens if item["categoria"] != "Sem categoria"},
        key=str.lower,
    )

    valor_estoque = sum(
        (Decimal(item["quantidade"]) * item["custo"] for item in itens),
        Decimal("0"),
    )

    reposicao = [item for item in itens if item["quantidade"] <= item["minimo"]]
    em_falta = [item for item in reposicao if item["quantidade"] <= 0]
    estoque_baixo = [item for item in reposicao if item["quantidade"] > 0]

    validade_itens = [
        item for item in itens
        if item["dias_validade"] is not None and 0 <= item["dias_validade"] <= 30
    ]
    validade_itens.sort(key=lambda item: item["dias_validade"])

    for item in validade_itens:
        item["status_text"] = "Vence hoje" if item["dias_validade"] == 0 else f"Em {item['dias_validade']} dias"

    reposicao_itens = sorted(
        reposicao,
        key=lambda item: (item["quantidade"] - item["minimo"], item["nome"]),
    )[:4]

    for item in reposicao_itens:
        item["sugestao"] = max(item["minimo"] * 2 - item["quantidade"], 1)
        item["valor_sugestao"] = Decimal(item["sugestao"]) * item["custo"]

    movimentacoes = MovimentacaoEstoque.objects.select_related("produto", "usuario").order_by("-data_movimentacao", "-id")[:12]

    context = {
        "estoques": itens,
        "categorias": categorias,
        "total_produtos": len(itens),
        "valor_estoque": valor_estoque,
        "variacao_estoque": "+4,2%",
        "reposicao_total": len(reposicao),
        "estoque_baixo": len(estoque_baixo),
        "estoque_falta": len(em_falta),
        "vencendo_7_dias": len([item for item in itens if item["dias_validade"] is not None and 0 <= item["dias_validade"] <= 7]),
        "vencimentos_count": len(validade_itens),
        "validade_itens": validade_itens[:4],
        "reposicao_itens": reposicao_itens,
        "movimentacoes": movimentacoes,
        "atualizado_em": timezone.localtime().strftime("%H:%M"),
    }
    return render(request, "privado/estoque.html", context)


@login_required
@require_POST
def registrar_entrada(request):
    produto = get_object_or_404(Produto, pk=request.POST.get("produto_id"))
    quantidade = int(_decimal(request.POST.get("quantidade")))

    if quantidade <= 0:
        return JsonResponse({"sucesso": False, "mensagem": "Informe uma quantidade maior que zero."}, status=400)

    with transaction.atomic():
        anterior = int(produto.quantidade or 0)
        novo = anterior + quantidade
        _save_quantity(produto, novo)
        _registrar_movimento(request, produto, "entrada", quantidade, anterior, novo, request.POST.get("fornecedor", ""))

        # Registra também o lote no modelo Estoque já existente.
        if Mercadinho is not None:
            mercadinho = Mercadinho.objects.first()
            validade = request.POST.get("validade") or ""
            if mercadinho and validade:
                categoria = str(getattr(produto, "categoria", "Sem categoria") or "Sem categoria")
                Estoque.objects.create(
                    produto=produto,
                    mercadinho=mercadinho,
                    categoria=categoria,
                    validade=validade,
                    fornecedor=request.POST.get("fornecedor", ""),
                    quantidade=quantidade,
                    data_entrada=date.today(),
                )

    return JsonResponse({"sucesso": True, "mensagem": "Entrada registrada com sucesso.", "novo_estoque": novo})


@login_required
@require_POST
def registrar_saida(request):
    produto = get_object_or_404(Produto, pk=request.POST.get("produto_id"))
    quantidade = int(_decimal(request.POST.get("quantidade")))
    anterior = int(produto.quantidade or 0)

    if quantidade <= 0:
        return JsonResponse({"sucesso": False, "mensagem": "Informe uma quantidade maior que zero."}, status=400)
    if quantidade > anterior:
        return JsonResponse({"sucesso": False, "mensagem": "A quantidade da saída é maior que o estoque disponível."}, status=400)

    with transaction.atomic():
        novo = anterior - quantidade
        _save_quantity(produto, novo)
        _registrar_movimento(request, produto, "saida", quantidade, anterior, novo, "Saída manual")

    return JsonResponse({"sucesso": True, "mensagem": "Saída registrada com sucesso.", "novo_estoque": novo})


@login_required
@require_POST
def ajustar_estoque(request):
    produto = get_object_or_404(Produto, pk=request.POST.get("produto_id"))
    novo = int(_decimal(request.POST.get("novo_estoque"), Decimal("-1")))
    anterior = int(produto.quantidade or 0)

    if novo < 0:
        return JsonResponse({"sucesso": False, "mensagem": "Informe um novo estoque válido."}, status=400)

    with transaction.atomic():
        _save_quantity(produto, novo)
        _registrar_movimento(request, produto, "ajuste", abs(novo - anterior), anterior, novo, "Ajuste de inventário")

    return JsonResponse({"sucesso": True, "mensagem": "Estoque ajustado com sucesso.", "novo_estoque": novo})


@login_required
def exportar_csv(request):
    itens = [_normalize(produto) for produto in Produto.objects.all().order_by("nome")]
    q = request.GET.get("q", "").strip().lower()
    categoria = request.GET.get("categoria", "").strip().lower()
    status = request.GET.get("status", "").strip().lower()

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="estoque_mercadonex.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Produto", "Código", "Categoria", "Quantidade", "Estoque mínimo", "Unidade", "Custo unitário", "Validade", "Status"])

    for item in itens:
        if q and q not in item["nome"].lower() and q not in item["codigo"].lower():
            continue
        if categoria and item["categoria"].lower() != categoria:
            continue
        if status and item["status"] != status:
            continue
        writer.writerow([
            item["nome"], item["codigo"], item["categoria"], item["quantidade"],
            item["minimo"], item["unidade"], f'{item["custo"]:.2f}',
            item["validade"], item["status_label"],
        ])

    return response
