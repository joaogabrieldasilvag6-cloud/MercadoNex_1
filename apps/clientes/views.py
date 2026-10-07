from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from decimal import Decimal

from apps.vendas.models import Venda
from .models import Cliente


@login_required
def clientes(request):
    hoje = timezone.localdate()

    dividas_vencidas = Venda.objects.filter(
        cliente=OuterRef("pk"),
        forma_pagamento="FIADO",
        status="FINALIZADA",
        fiado_pago=False,
        vencimento_fiado__lt=hoje,
    )

    clientes_qs = Cliente.objects.annotate(
        inadimplente=Exists(dividas_vencidas)
    ).order_by("-id")

    clientes_ativos = clientes_qs.filter(ativo_fiado=True).count()
    clientes_inadimplentes = clientes_qs.filter(
        ativo_fiado=True,
        inadimplente=True,
    ).count()
    clientes_bloqueados = clientes_qs.filter(ativo_fiado=False).count()

    total_fiado = clientes_qs.aggregate(
        total=Sum("saldo_fiado")
    )["total"] or Decimal("0.00")

    return render(
        request,
        "privado/clientes.html",
        {
            "clientes": clientes_qs,
            "clientes_ativos": clientes_ativos,
            "clientes_bloqueados": clientes_bloqueados,
            "clientes_inadimplentes": clientes_inadimplentes,
            "total_fiado": total_fiado,
        },
    )


@login_required
@require_POST
def cadastrar_cliente(request):
    try:
        limite_fiado = request.POST.get("limite_fiado") or 0

        cliente = Cliente.objects.create(
            nome=request.POST.get("nome", "").strip(),
            telefone=request.POST.get("telefone", "").strip(),
            email=request.POST.get("email", "").strip() or None,
            cpf=request.POST.get("cpf", "").strip(),
            endereco=request.POST.get("endereco", "").strip(),
            limite_fiado=limite_fiado,
            ativo_fiado=request.POST.get("ativo_fiado") == "on",
        )

        return JsonResponse({
            "success": True,
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "email": cliente.email or "",
                "cpf": cliente.cpf,
                "endereco": cliente.endereco,
                "saldo": float(cliente.saldo_fiado),
                "limite_fiado": float(cliente.limite_fiado),
                "ativo_fiado": cliente.ativo_fiado,
            },
        })

    except IntegrityError:
        return JsonResponse({
            "success": False,
            "erro": "Já existe um cliente cadastrado com este CPF.",
        }, status=400)


@login_required
@require_POST
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    nome = cliente.nome
    cliente.delete()

    return JsonResponse({
        "success": True,
        "id": id,
        "mensagem": f"Cliente {nome} removido com sucesso.",
    })


@login_required
@require_POST
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    try:
        cliente.nome = request.POST.get("nome", "").strip()
        cliente.telefone = request.POST.get("telefone", "").strip()
        cliente.email = request.POST.get("email", "").strip() or None
        cliente.cpf = request.POST.get("cpf", "").strip()
        cliente.endereco = request.POST.get("endereco", "").strip()
        cliente.limite_fiado = request.POST.get("limite_fiado") or 0
        cliente.ativo_fiado = request.POST.get("ativo_fiado") == "on"
        cliente.save()

        return JsonResponse({
            "success": True,
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "email": cliente.email or "",
                "cpf": cliente.cpf,
                "endereco": cliente.endereco,
                "saldo": float(cliente.saldo_fiado),
                "limite_fiado": float(cliente.limite_fiado),
                "ativo_fiado": cliente.ativo_fiado,
            },
        })

    except IntegrityError:
        return JsonResponse({
            "success": False,
            "erro": "Já existe outro cliente cadastrado com este CPF.",
        }, status=400)


@login_required
def cliente_json(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    return JsonResponse({
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email or "",
        "cpf": cliente.cpf,
        "endereco": cliente.endereco,
        "limite_fiado": float(cliente.limite_fiado),
        "ativo_fiado": cliente.ativo_fiado,
    })


@login_required
@require_POST
def alternar_bloqueio_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.ativo_fiado = not cliente.ativo_fiado
    cliente.save(update_fields=["ativo_fiado"])

    return JsonResponse({
        "success": True,
        "id": cliente.id,
        "bloqueado": not cliente.ativo_fiado,
        "ativo_fiado": cliente.ativo_fiado,
        "mensagem": (
            "Cliente bloqueado com sucesso."
            if not cliente.ativo_fiado
            else "Cliente desbloqueado com sucesso."
        ),
    })


@login_required
@require_POST
@transaction.atomic
def quitar_fiado_cliente(request, id):
    cliente = get_object_or_404(
        Cliente.objects.select_for_update(),
        id=id,
    )

    dividas = list(
        Venda.objects.select_for_update().filter(
            cliente=cliente,
            forma_pagamento="FIADO",
            status="FINALIZADA",
            fiado_pago=False,
        )
    )

    if not dividas:
        return JsonResponse({
            "success": False,
            "erro": "Este cliente não possui fiado em aberto.",
        }, status=400)

    valor_pago = sum(
        (Decimal(venda.valor_final or 0) for venda in dividas),
        Decimal("0.00"),
    )

    cliente.saldo_fiado = max(
        Decimal("0.00"),
        Decimal(cliente.saldo_fiado or 0) - valor_pago,
    )
    cliente.save(update_fields=["saldo_fiado"])

    agora = timezone.now()
    Venda.objects.filter(id__in=[v.id for v in dividas]).update(
        fiado_pago=True,
        data_pagamento_fiado=agora,
    )

    return JsonResponse({
        "success": True,
        "cliente": cliente.nome,
        "valor_pago": str(valor_pago),
        "novo_saldo_fiado": str(cliente.saldo_fiado),
    })
