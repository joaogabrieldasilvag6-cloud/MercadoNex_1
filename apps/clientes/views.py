from django.shortcuts import render
from .models import Cliente
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Sum


@login_required
def clientes(request):

    clientes = Cliente.objects.all().order_by("-id")

    clientes_ativos = clientes.filter(ativo_fiado=True).count()

    clientes_bloqueados = clientes.filter(ativo_fiado=False).count()

    total_fiado = clientes.aggregate(
        total=Sum("saldo_fiado")
    )["total"] or 0

    context = {
        "clientes": clientes,
        "clientes_ativos": clientes_ativos,
        "clientes_bloqueados": clientes_bloqueados,
        "total_fiado": total_fiado,
    }

    return render(request, "privado/clientes.html", context)

@login_required
def cadastrar_cliente(request):

    if request.method == "POST":

        try:

            cliente = Cliente.objects.create(
                nome=request.POST.get("nome"),
                telefone=request.POST.get("telefone"),
                email=request.POST.get("email"),
                cpf=request.POST.get("cpf"),
                endereco=request.POST.get("endereco"),
                limite_fiado=request.POST.get("limite_fiado") or 0,
                ativo_fiado=request.POST.get("ativo_fiado") == "on"
            )

            return JsonResponse({
                "success": True,
                "cliente": {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "telefone": cliente.telefone,
                    "email": cliente.email,
                    "saldo": float(cliente.saldo_fiado),
                    "ativo_fiado": cliente.ativo_fiado,
                }
            })

        except IntegrityError:

            return JsonResponse({
                "success": False,
                "erro": "Já existe um cliente cadastrado com este CPF."
            })

    return JsonResponse({
        "success": False
    })

@login_required
def excluir_cliente(request, id):

    cliente = get_object_or_404(Cliente, id=id)

    cliente.delete()

    return JsonResponse({
        "success": True,
        "id": id
    })

@login_required
def editar_cliente(request, id):

    cliente = get_object_or_404(Cliente, id=id)

    if request.method == "POST":

        cliente.nome = request.POST.get("nome")
        cliente.telefone = request.POST.get("telefone")
        cliente.email = request.POST.get("email")
        cliente.cpf = request.POST.get("cpf")
        cliente.endereco = request.POST.get("endereco")
        cliente.limite_fiado = request.POST.get("limite_fiado") or 0
        cliente.ativo_fiado = request.POST.get("ativo_fiado") == "on"

        cliente.save()

        return JsonResponse({
            "success": True,
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "email": cliente.email,
                "saldo": float(cliente.saldo_fiado),
                "ativo_fiado": cliente.ativo_fiado,
            }
        })

    return JsonResponse({
        "success": False
    })

def cliente_json(request, id):

    cliente = Cliente.objects.get(id=id)

    return JsonResponse({
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email,
        "cpf": cliente.cpf,
        "endereco": cliente.endereco,
        "limite_fiado": float(cliente.limite_fiado),
        "ativo_fiado": cliente.ativo_fiado,
    })
