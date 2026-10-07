from django.shortcuts import render
import csv
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Movimentacao


def _parse_date(value, fallback):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback


def _periodo(request):
    hoje = date.today()
    inicio = _parse_date(request.GET.get("inicio"), hoje - timedelta(days=29))
    fim = _parse_date(request.GET.get("fim"), hoje)

    if inicio > fim:
        inicio, fim = fim, inicio

    return inicio, fim


def _get_mercadinho(request):
    return getattr(request.user, "mercadinho", None)


@login_required
def financeiro(request):
    inicio, fim = _periodo(request)
    mercadinho = _get_mercadinho(request)

    qs = Movimentacao.objects.filter(data__range=(inicio, fim))
    if mercadinho is not None:
        qs = qs.filter(mercadinho=mercadinho)

    entradas = qs.filter(tipo=Movimentacao.Tipo.ENTRADA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")

    saidas = qs.filter(tipo=Movimentacao.Tipo.SAIDA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")

    resultado = entradas - saidas
    margem = (resultado / entradas * 100) if entradas else Decimal("0.00")

    saldo_qs = Movimentacao.objects.all()
    if mercadinho is not None:
        saldo_qs = saldo_qs.filter(mercadinho=mercadinho)

    saldo_entradas = saldo_qs.filter(tipo=Movimentacao.Tipo.ENTRADA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    saldo_saidas = saldo_qs.filter(tipo=Movimentacao.Tipo.SAIDA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    saldo = saldo_entradas - saldo_saidas

    contas = qs.exclude(status=Movimentacao.Status.PAGA)
    contas_pagas = qs.filter(status=Movimentacao.Status.PAGA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    contas_a_vencer = contas.filter(status=Movimentacao.Status.A_VENCER).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    contas_atrasadas = contas.filter(status=Movimentacao.Status.ATRASADA).aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")

    movimentos = qs[:8]

    context = {
        "mercadinho": mercadinho,
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "inicio_formatado": inicio.strftime("%d/%m/%Y"),
        "fim_formatado": fim.strftime("%d/%m/%Y"),
        "entradas": entradas,
        "saidas": saidas,
        "resultado": resultado,
        "margem": margem,
        "saldo": saldo,
        "movimentos": movimentos,
        "contas_pagas": contas_pagas,
        "contas_a_vencer": contas_a_vencer,
        "contas_atrasadas": contas_atrasadas,
        "contas_total": contas_pagas + contas_a_vencer + contas_atrasadas,
    }
    return render(request, "privado/financeiro.html", context)


@login_required
def nova_movimentacao(request):
    if request.method != "POST":
        return redirect("financeiro:financeiro")

    descricao = request.POST.get("descricao", "").strip()
    tipo = request.POST.get("tipo", "").upper()
    valor_texto = request.POST.get("valor", "").replace(",", ".")
    categoria = request.POST.get("categoria", "").strip()
    data = _parse_date(request.POST.get("data"), date.today())
    vencimento = request.POST.get("data_vencimento") or None
    forma = request.POST.get("forma_pagamento", "").strip()
    status = request.POST.get("status", Movimentacao.Status.PAGA)

    try:
        valor = Decimal(valor_texto)
    except Exception:
        valor = Decimal("0")

    if not descricao or tipo not in (Movimentacao.Tipo.ENTRADA, Movimentacao.Tipo.SAIDA) or valor <= 0:
        messages.error(request, "Preencha os dados da movimentação corretamente.")
        return redirect("financeiro:financeiro")

    movimentacao = Movimentacao(
        mercadinho=_get_mercadinho(request),
        descricao=descricao,
        tipo=tipo,
        valor=valor,
        categoria=categoria,
        data=data,
        data_vencimento=vencimento,
        forma_pagamento=forma,
        status=status,
        referencia=request.POST.get("referencia", "").strip(),
        observacao=request.POST.get("observacao", "").strip(),
    )
    movimentacao.save()

    messages.success(request, "Movimentação adicionada com sucesso.")
    return redirect("financeiro:financeiro")


@login_required
def excluir_movimentacao(request, pk):
    if request.method != "POST":
        return redirect("financeiro:financeiro")

    qs = Movimentacao.objects.filter(pk=pk)
    mercadinho = _get_mercadinho(request)
    if mercadinho is not None:
        qs = qs.filter(mercadinho=mercadinho)

    movimentacao = get_object_or_404(qs)
    movimentacao.delete()
    messages.success(request, "Movimentação excluída.")
    return redirect("financeiro:financeiro")


@login_required
def exportar_csv(request):
    inicio, fim = _periodo(request)
    mercadinho = _get_mercadinho(request)

    qs = Movimentacao.objects.filter(data__range=(inicio, fim))
    if mercadinho is not None:
        qs = qs.filter(mercadinho=mercadinho)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="mercadonex_financeiro.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "Data", "Tipo", "Descrição", "Categoria", "Valor",
        "Forma de pagamento", "Status", "Referência"
    ])

    for item in qs:
        writer.writerow([
            item.data.strftime("%d/%m/%Y"),
            item.get_tipo_display(),
            item.descricao,
            item.categoria,
            f"{item.valor:.2f}".replace(".", ","),
            item.forma_pagamento,
            item.get_status_display(),
            item.referencia,
        ])

    return response


@login_required
def api_resumo(request):
    inicio, fim = _periodo(request)
    qs = Movimentacao.objects.filter(data__range=(inicio, fim))

    entradas = qs.filter(tipo=Movimentacao.Tipo.ENTRADA).aggregate(total=Sum("valor"))["total"] or Decimal("0")
    saidas = qs.filter(tipo=Movimentacao.Tipo.SAIDA).aggregate(total=Sum("valor"))["total"] or Decimal("0")

    return JsonResponse({
        "entradas": float(entradas),
        "saidas": float(saidas),
        "resultado": float(entradas - saidas),
    })
