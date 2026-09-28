from django.shortcuts import render,  redirect
from .models import Produto
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages



@login_required
def produtos(request):
    produtos_queryset = Produto.objects.all().order_by("-id")

    buscar = request.GET.get("buscar", "").strip()
    if buscar:
        produtos_queryset = produtos_queryset.filter(
            Q(nome__icontains=buscar) | Q(codigo__icontains=buscar)
        )

    categoria = request.GET.get("categoria", "").strip()
    if categoria:
        produtos_queryset = produtos_queryset.filter(categoria=categoria)

    status = request.GET.get("status", "").strip()
    if status == "ativo":
        produtos_queryset = produtos_queryset.filter(status=True)
    elif status == "inativo":
        produtos_queryset = produtos_queryset.filter(status=False)

    total_produtos = Produto.objects.count()
    estoque_baixo = Produto.objects.filter(quantidade__gt=0, quantidade__lte=10).count()
    sem_estoque = Produto.objects.filter(quantidade=0).count()

    paginator = Paginator(produtos_queryset, 10)
    produtos = paginator.get_page(request.GET.get("page"))

    context = {
        "produtos": produtos,
        "buscar": buscar,
        "categoria": categoria,
        "status": status,
        "total_produtos": total_produtos,
        "estoque_baixo": estoque_baixo,
        "sem_estoque": sem_estoque,
    }
    return render(request, "privado/produtos.html", context)

@login_required
def cadastrar_produto(request):
    if request.method == "POST":
        produto = Produto(
            nome=request.POST.get("nome", "").strip(),
            categoria=request.POST.get("categoria", "").strip(),
            descricao=request.POST.get("descricao", "").strip(),
            codigo=request.POST.get("codigo", "").strip(),
            marca=request.POST.get("marca", "").strip(),
            preco_venda=request.POST.get("preco_venda") or 0,
            preco_custo=request.POST.get("preco_custo") or None,
            quantidade=request.POST.get("quantidade") or 0,
            validade=request.POST.get("validade") or None,
            fornecedor=request.POST.get("fornecedor", "").strip(),
            status=bool(request.POST.get("status")),
            destaque=bool(request.POST.get("destaque")),
        )
        if request.FILES.get("imagem"):
            produto.imagem = request.FILES["imagem"]
        produto.save()
        messages.success(request, "Produto cadastrado com sucesso!")
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
        produto.nome = request.POST.get("nome", "").strip()
        produto.categoria = request.POST.get("categoria", "").strip()
        produto.descricao = request.POST.get("descricao", "").strip()
        produto.codigo = request.POST.get("codigo", "").strip()
        produto.marca = request.POST.get("marca", "").strip()

        produto.preco_venda = request.POST.get("preco_venda") or 0
        produto.preco_custo = request.POST.get("preco_custo") or None
        produto.quantidade = request.POST.get("quantidade") or 0
        produto.validade = request.POST.get("validade") or None

        produto.fornecedor = request.POST.get("fornecedor", "").strip()

        produto.status = bool(request.POST.get("status"))
        produto.destaque = bool(request.POST.get("destaque"))

        if request.FILES.get("imagem"):
            produto.imagem = request.FILES["imagem"]

        produto.save()

        messages.success(request, "Produto atualizado com sucesso!")

        return redirect("produtos")

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
def produto_json(request, id):
    produto = get_object_or_404(Produto, id=id)
    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome or "",
        "categoria": produto.categoria or "",
        "descricao": produto.descricao or "",
        "codigo": produto.codigo or "",
        "marca": produto.marca or "",
        "preco_venda": str(produto.preco_venda) if produto.preco_venda is not None else "",
        "preco_custo": str(produto.preco_custo) if produto.preco_custo is not None else "",
        "quantidade": produto.quantidade,
        "validade": produto.validade.strftime("%Y-%m-%d") if produto.validade else "",
        "fornecedor": produto.fornecedor or "",
        "status": produto.status,
        "destaque": produto.destaque,
    })


