from django.shortcuts import render, redirect
from .models import Cliente, Produto, Venda
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.db.models import Sum



def inicial(request):
    return render(request, 'index.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        print("Usuário:", username)
        print("Senha:", password)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("Resultado authenticate:", user)

        if user is not None:
            login(request, user)
            print("Login realizado!")
            return redirect('dashboard')

        print("Usuário ou senha inválidos")

        return render(
            request,
            'privado/login.html',
            {'erro': 'Usuário ou senha inválidos'}
        )

    return render(request, 'privado/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def cadastro(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmar = request.POST.get('confirmar')

        if password != confirmar:
            return render(
                request,
                'privado/cadastro.html',
                {'erro': 'As senhas não coincidem'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'privado/cadastro.html',
                {'erro': 'Usuário já existe'}
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'privado/cadastro.html')


@login_required
def dashboard(request):

    produtos = Produto.objects.all().order_by("-id")
    clientes = Cliente.objects.all().order_by("-id")

    return render(
        request,
        "dashboard.html",
        {
            "produtos": produtos,
            "clientes": clientes,
        }
    )

@login_required
def produtos(request):

    produtos = Produto.objects.all().order_by("-id")

    buscar = request.GET.get("buscar")

    if buscar:
        produtos = produtos.filter(
            Q(nome__icontains=buscar) |
            Q(codigo__icontains=buscar)
        )

    categoria = request.GET.get("categoria")

    if categoria:
        produtos = produtos.filter(categoria=categoria)

    status = request.GET.get("status")

    if status == "ativo":
        produtos = produtos.filter(status=True)

    elif status == "inativo":
        produtos = produtos.filter(status=False)


    total_produtos = Produto.objects.count()

    produtos_ativos = Produto.objects.filter(
        status=True
    ).count()

    estoque_baixo = Produto.objects.filter(
        quantidade__lte=10
    ).count()

    produtos_destaque = Produto.objects.filter(
        destaque=True
    ).count()


    paginator = Paginator(produtos, 10)
    page = request.GET.get("page")
    produtos = paginator.get_page(page)
    context = {

        "produtos": produtos,
        "buscar": buscar,
        "categoria": categoria,
        "status": status,
        "total_produtos": total_produtos,
        "produtos_ativos": produtos_ativos,
        "estoque_baixo": estoque_baixo,
        "produtos_destaque": produtos_destaque,

    }

    return render(
        request,
        "produtos/produtos.html",
        context
    )

@login_required
def cadastrar_produto(request):

    if request.method == "POST":

        Produto.objects.create(
            nome=request.POST.get("nome"),
            categoria=request.POST.get("categoria"),
            descricao=request.POST.get("descricao"),
            codigo=request.POST.get("codigo"),
            marca=request.POST.get("marca"),
            preco_venda=request.POST.get("preco_venda"),
            preco_custo=request.POST.get("preco_custo") or None,
            quantidade=request.POST.get("quantidade"),
            validade=request.POST.get("validade") or None,
            fornecedor=request.POST.get("fornecedor"),
            status=bool(request.POST.get("status")),
            destaque=bool(request.POST.get("destaque")),
        )

        messages.success(request, "Produto cadastrado com sucesso!")
        return redirect("produtos")

    return redirect("produtos")


@login_required
def excluir_produto(request, id):

    produto = get_object_or_404(Produto, id=id)
    produto.delete()

    messages.success(request, "Produto removido com sucesso!")

    return redirect("produtos")


@login_required
def editar_produto(request, id):

    produto = get_object_or_404(Produto, id=id)

    if request.method == "POST":

        produto.nome = request.POST.get("nome")
        produto.categoria = request.POST.get("categoria")
        produto.descricao = request.POST.get("descricao")
        produto.codigo = request.POST.get("codigo")
        produto.marca = request.POST.get("marca")
        produto.preco_venda = request.POST.get("preco_venda")
        produto.preco_custo = request.POST.get("preco_custo") or None
        produto.quantidade = request.POST.get("quantidade")
        produto.validade = request.POST.get("validade") or None
        produto.fornecedor = request.POST.get("fornecedor")

        produto.status = bool(request.POST.get("status"))
        produto.destaque = bool(request.POST.get("destaque"))

        produto.save()

        messages.success(request, "Produto atualizado com sucesso!")

        return redirect("produtos")

    produtos = Produto.objects.all().order_by("-id")

    context = {
        "produtos": produtos,
        "produto_edicao": produto,
        "total_produtos": produtos.count(),
        "produtos_ativos": produtos.filter(status=True).count(),
        "estoque_baixo": produtos.filter(quantidade__lte=10).count(),
        "produtos_destaque": produtos.filter(destaque=True).count(),
    }

    return render(request, "produtos/produtos.html", context)


@login_required
def produto_json(request, id):

    produto = get_object_or_404(Produto, id=id)

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "categoria": produto.categoria,
        "descricao": produto.descricao,
        "codigo": produto.codigo,
        "marca": produto.marca,
        "preco_venda": str(produto.preco_venda),
        "preco_custo": str(produto.preco_custo or ""),
        "quantidade": produto.quantidade,
        "validade": produto.validade.strftime("%Y-%m-%d") if produto.validade else "",
        "fornecedor": produto.fornecedor,
        "status": produto.status,
        "destaque": produto.destaque,
    })


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

    return render(request, "clientes/clientes.html", context)

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


@login_required
def vendas(request):

    clientes = Cliente.objects.all().order_by("nome")
    produtos = Produto.objects.filter(status=True).order_by("nome")
    vendas = Venda.objects.all().order_by("-data")
    context = {
        "clientes": clientes,
        "produtos": produtos,
        "vendas": vendas,
    }

    return render(request, "componentes/vendas.html", context)

@require_POST
def finalizar_venda(request):

    try:

        dados = json.loads(request.body)

        return JsonResponse({
            "sucesso": True,
            "mensagem": "Dados recebidos com sucesso!",
            "dados": dados
        })

    except Exception as erro:

        return JsonResponse({
            "sucesso": False,
            "erro": str(erro)
        }, status=400)