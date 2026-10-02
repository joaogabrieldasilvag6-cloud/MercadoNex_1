from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


@login_required
def configuracoes(request):
    return render(request, "privado/configuracoes.html")


@login_required
@require_POST
def salvar_configuracoes(request):

    try:
        dados = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Dados de configuração inválidos."
            },
            status=400
        )

    configuracoes_permitidas = {
        "tema": ["claro", "escuro"],
        "fonte": ["small", "medium", "large"],
        "compacto": [True, False],
        "animacoes": [True, False],
        "estoque": [True, False],
        "fiado": [True, False],
    }

    dados_validos = {}

    for campo, valores in configuracoes_permitidas.items():

        if campo not in dados:
            continue

        valor = dados[campo]

        if valor in valores:
            dados_validos[campo] = valor

    configuracoes_atuais = request.session.get(
        "mercadonex_configuracoes",
        {}
    )

    configuracoes_atuais.update(dados_validos)

    request.session["mercadonex_configuracoes"] = configuracoes_atuais
    request.session.modified = True

    return JsonResponse(
        {
            "sucesso": True,
            "mensagem": "Configurações salvas com sucesso.",
            "configuracoes": configuracoes_atuais
        }
    )
