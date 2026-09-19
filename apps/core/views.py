from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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





