from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from apps.vendas.models import Venda, ItemVenda
from apps.clientes.models import Cliente
from apps.produtos.models import Produto


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

    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    inicio_30d = hoje - timedelta(days=29)

    vendas_finalizadas = Venda.objects.filter(status="FINALIZADA")
    vendas_hoje_qs = vendas_finalizadas.filter(data__date=hoje)
    vendas_mes_qs = vendas_finalizadas.filter(data__date__gte=inicio_mes, data__date__lte=hoje)
    vendas_semana_qs = vendas_finalizadas.filter(data__date__gte=inicio_semana, data__date__lte=fim_semana)

    receita_hoje = vendas_hoje_qs.aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    receita_mes = vendas_mes_qs.aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    receita_semana = vendas_semana_qs.aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")

    vendas_hoje = vendas_hoje_qs.count()
    vendas_mes = vendas_mes_qs.count()
    transacoes_semana = vendas_semana_qs.count()
    ticket_medio_semana = receita_semana / transacoes_semana if transacoes_semana else Decimal("0.00")
    ticket_medio_mes = receita_mes / vendas_mes if vendas_mes else Decimal("0.00")

    clientes_qs = Cliente.objects.all()
    clientes_total = clientes_qs.count()
    clientes_ativos = clientes_qs.filter(ativo_fiado=True).count()
    novos_clientes_semana = clientes_qs.filter(
        data_cadastro__date__gte=inicio_semana,
        data_cadastro__date__lte=fim_semana
    ).count()
    clientes_ativos_30d = clientes_qs.filter(
        vendas__status="FINALIZADA",
        vendas__data__date__gte=inicio_30d,
        vendas__data__date__lte=hoje
    ).distinct().count()

    produtos_qs = Produto.objects.all()
    produtos_total = produtos_qs.count()
    itens_em_falta = produtos_qs.filter(quantidade__lte=10).count()
    estoque_baixo = produtos_qs.filter(quantidade__lte=10, status=True).order_by("quantidade", "nome")[:4]

    vendas_recentes = list(
        vendas_finalizadas
        .select_related("cliente")
        .annotate(total_itens=Coalesce(Sum("itens__quantidade"), 0))
        .order_by("-data")[:6]
    )

    pagamento_nomes = {
        "PIX": ("PIX", "pix"),
        "DINHEIRO": ("Dinheiro", "cash"),
        "CARTAO": ("Cartão", "debit"),
        "DEBITO": ("Débito", "debit"),
        "CREDITO": ("Crédito", "credit"),
        "FIADO": ("Fiado", "fiado"),
    }
    for venda in vendas_recentes:
        nome, classe = pagamento_nomes.get(
            venda.forma_pagamento,
            (venda.forma_pagamento.title() if venda.forma_pagamento else "Não informado", "cash")
        )
        venda.pagamento_nome = nome
        venda.pagamento_classe = classe

    mais_vendidos = list(
        ItemVenda.objects
        .filter(venda__status="FINALIZADA")
        .values("produto__nome", "produto__categoria")
        .annotate(
            quantidade_total=Coalesce(Sum("quantidade"), 0),
            faturamento=Coalesce(Sum("subtotal"), Decimal("0.00")),
        )
        .order_by("-quantidade_total", "-faturamento")[:5]
    )

    vendas_por_dia = {
        item["dia"]: item["total"]
        for item in vendas_semana_qs
        .annotate(dia=TruncDate("data"))
        .values("dia")
        .annotate(total=Coalesce(Sum("valor_final"), Decimal("0.00")))
    }
    maior_dia = max([Decimal(str(valor)) for valor in vendas_por_dia.values()] or [Decimal("1")])
    nomes_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    vendas_semana = []
    for indice in range(7):
        dia = inicio_semana + timedelta(days=indice)
        valor = Decimal(str(vendas_por_dia.get(dia, Decimal("0.00")) or 0))
        altura = int((valor / maior_dia * Decimal("100")) if maior_dia else 0)
        vendas_semana.append({"nome": nomes_dias[indice], "valor": valor, "altura": max(8, altura) if valor else 5})

    pagamentos_counts = (
        vendas_mes_qs
        .values("forma_pagamento")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    pagamentos_mes = []
    for item in pagamentos_counts:
        nome, _ = pagamento_nomes.get(item["forma_pagamento"], (item["forma_pagamento"], "cash"))
        percentual = round((item["total"] / vendas_mes) * 100) if vendas_mes else 0
        pagamentos_mes.append({"nome": nome, "percentual": percentual})
    if not pagamentos_mes:
        pagamentos_mes = [
            {"nome": "PIX", "percentual": 0},
            {"nome": "Débito", "percentual": 0},
            {"nome": "Crédito", "percentual": 0},
            {"nome": "Dinheiro", "percentual": 0},
        ]

    lucro_estimado_mes = Decimal("0.00")
    itens_mes = (
        ItemVenda.objects
        .filter(venda__status="FINALIZADA", venda__data__date__gte=inicio_mes, venda__data__date__lte=hoje)
        .select_related("produto")
    )
    for item in itens_mes:
        custo = item.produto.preco_custo or Decimal("0.00")
        lucro_estimado_mes += (item.preco_unitario - custo) * item.quantidade

    clientes_frequentes = list(
        clientes_qs
        .annotate(
            visitas=Count("vendas", filter=Q(vendas__status="FINALIZADA"), distinct=True),
            total_gasto=Coalesce(Sum("vendas__valor_final", filter=Q(vendas__status="FINALIZADA")), Decimal("0.00")),
            primeira_compra=Min("vendas__data", filter=Q(vendas__status="FINALIZADA")),
        )
        .filter(visitas__gt=0)
        .order_by("-visitas", "-total_gasto")[:5]
    )

    clientes_novos = list(clientes_qs.order_by("-data_cadastro")[:4])
    for cliente in clientes_novos:
        primeira = cliente.vendas.filter(status="FINALIZADA").order_by("data").first()
        cliente.primeira_compra = (
            f"1ª compra: R$ {primeira.valor_final:.2f}".replace(".", ",")
            if primeira else "Ainda sem compra"
        )

    produto_critico = produtos_qs.filter(status=True, quantidade__lte=5).order_by("quantidade", "nome").first()
    if produto_critico:
        estoque_critico_texto = f"{produto_critico.nome} tem apenas {produto_critico.quantidade} unidade(s) disponível(is)."
    elif estoque_baixo:
        estoque_critico_texto = f"{len(estoque_baixo)} produto(s) estão com estoque abaixo do mínimo definido."
    else:
        estoque_critico_texto = "Nenhum produto está em nível crítico de estoque no momento."

    vendas_7d = vendas_finalizadas.filter(
        data__date__gte=hoje - timedelta(days=6),
        data__date__lte=hoje,
    ).count()
    vendas_alerta_texto = (
        f"{vendas_7d} venda(s) finalizada(s) nos últimos 7 dias."
        if vendas_7d else
        "Ainda não há vendas finalizadas nos últimos 7 dias."
    )

    return render(
        request,
        "dashboard.html",
        {
            "hoje": hoje,
            "receita_hoje": receita_hoje,
            "receita_mes": receita_mes,
            "vendas_hoje": vendas_hoje,
            "vendas_mes": vendas_mes,
            "clientes_ativos": clientes_ativos,
            "novos_clientes_semana": novos_clientes_semana,
            "itens_em_falta": itens_em_falta,
            "produtos_total": produtos_total,
            "vendas_recentes": vendas_recentes,
            "mais_vendidos": mais_vendidos,
            "estoque_baixo": estoque_baixo,
            "clientes_total": clientes_total,
            "clientes_ativos_30d": clientes_ativos_30d,
            "clientes_frequentes": clientes_frequentes,
            "clientes_novos": clientes_novos,
            "semana_inicio": inicio_semana,
            "semana_fim": fim_semana,
            "vendas_semana": vendas_semana,
            "receita_semana": receita_semana,
            "ticket_medio_semana": ticket_medio_semana,
            "transacoes_semana": transacoes_semana,
            "pagamentos_mes": pagamentos_mes,
            "lucro_estimado_mes": lucro_estimado_mes,
            "ticket_medio_mes": ticket_medio_mes,
            "estoque_critico_texto": estoque_critico_texto,
            "vendas_alerta_texto": vendas_alerta_texto,
        }
    )





