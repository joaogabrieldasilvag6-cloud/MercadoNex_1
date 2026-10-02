from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.core.models import Mercadinho
from .models import PerfilUsuario


def obter_perfil(user):
    perfil, criado = PerfilUsuario.objects.get_or_create(
        usuario=user,
        defaults={
            'nome_completo': user.get_full_name(),
        }
    )

    if criado:
        perfil.nome_completo = user.get_full_name()
        perfil.save(update_fields=['nome_completo'])

    return perfil


def dados_perfil(perfil):
    user = perfil.usuario

    return {
        'id': perfil.id,
        'username': user.username,
        'email': user.email,
        'nome_completo': perfil.nome_completo or user.get_full_name(),
        'telefone': perfil.telefone,
        'tipo': perfil.get_tipo_display(),
        'tipo_codigo': perfil.tipo,
        'status': user.is_active,
        'data_cadastro': user.date_joined.strftime('%d/%m/%Y'),
        'ultimo_acesso': user.last_login.strftime('%d/%m/%Y às %H:%M') if user.last_login else 'Ainda não registrado',
        'foto': perfil.foto.url if perfil.foto else '',
    }


def dados_mercadinho(mercado):
    if not mercado:
        return None

    return {
        'id': mercado.id,
        'nome': mercado.nome,
        'telefone': mercado.telefone,
        'email': mercado.email,
        'cnpj': mercado.cnpj,
        'localizacao': mercado.localizacao,
        'ativo': mercado.ativo,
    }


@login_required
def perfil(request):
    usuario = obter_perfil(request.user)

    return render(
        request,
        'privado/perfil.html',
        {
            'usuario': usuario,
            'mercado': usuario.mercadinho,
        }
    )


@login_required
@require_POST
def editar_perfil(request):
    perfil_usuario = obter_perfil(request.user)
    user = perfil_usuario.usuario

    nome_completo = request.POST.get('nome_completo', '').strip()
    email = request.POST.get('email', '').strip()
    telefone = request.POST.get('telefone', '').strip()

    if not nome_completo:
        return JsonResponse(
            {'success': False, 'erro': 'Informe seu nome completo.'},
            status=400
        )

    if len(nome_completo) > 150:
        return JsonResponse(
            {'success': False, 'erro': 'O nome completo deve ter no máximo 150 caracteres.'},
            status=400
        )

    user.email = email

    partes = nome_completo.split(maxsplit=1)
    user.first_name = partes[0]
    user.last_name = partes[1] if len(partes) > 1 else ''
    user.save(update_fields=['email', 'first_name', 'last_name'])

    perfil_usuario.nome_completo = nome_completo
    perfil_usuario.telefone = telefone
    perfil_usuario.save(update_fields=['nome_completo', 'telefone', 'data_atualizacao'])

    return JsonResponse({
        'success': True,
        'mensagem': 'Perfil atualizado com sucesso.',
        'usuario': dados_perfil(perfil_usuario),
    })


@login_required
@require_POST
def alterar_senha(request):
    user = request.user

    senha_atual = request.POST.get('senha_atual', '')
    nova_senha = request.POST.get('nova_senha', '')
    confirmar_senha = request.POST.get('confirmar_senha', '')

    if not user.check_password(senha_atual):
        return JsonResponse(
            {'success': False, 'erro': 'A senha atual está incorreta.'},
            status=400
        )

    if nova_senha != confirmar_senha:
        return JsonResponse(
            {'success': False, 'erro': 'As novas senhas não coincidem.'},
            status=400
        )

    if nova_senha == senha_atual:
        return JsonResponse(
            {'success': False, 'erro': 'A nova senha deve ser diferente da senha atual.'},
            status=400
        )

    try:
        validate_password(nova_senha, user)
    except ValidationError as erro:
        mensagem = ' '.join(erro.messages)
        return JsonResponse(
            {'success': False, 'erro': mensagem},
            status=400
        )

    user.set_password(nova_senha)
    user.save(update_fields=['password'])
    update_session_auth_hash(request, user)

    return JsonResponse({
        'success': True,
        'mensagem': 'Senha alterada com sucesso.'
    })


@login_required
@require_POST
def alterar_foto(request):
    perfil_usuario = obter_perfil(request.user)
    arquivo = request.FILES.get('foto')

    if not arquivo:
        return JsonResponse(
            {'success': False, 'erro': 'Selecione uma imagem.'},
            status=400
        )

    if arquivo.size > 5 * 1024 * 1024:
        return JsonResponse(
            {'success': False, 'erro': 'A imagem deve ter no máximo 5 MB.'},
            status=400
        )

    if not (arquivo.content_type or '').startswith('image/'):
        return JsonResponse(
            {'success': False, 'erro': 'Envie um arquivo de imagem válido.'},
            status=400
        )

    try:
        get_image_dimensions(arquivo)
        arquivo.seek(0)
    except Exception:
        return JsonResponse(
            {'success': False, 'erro': 'Não foi possível validar essa imagem.'},
            status=400
        )

    if perfil_usuario.foto:
        perfil_usuario.foto.delete(save=False)

    perfil_usuario.foto = arquivo
    perfil_usuario.save(update_fields=['foto', 'data_atualizacao'])

    return JsonResponse({
        'success': True,
        'mensagem': 'Foto atualizada com sucesso.',
        'foto': perfil_usuario.foto.url,
    })


@login_required
@require_POST
def remover_foto(request):
    perfil_usuario = obter_perfil(request.user)

    if perfil_usuario.foto:
        perfil_usuario.foto.delete(save=False)
        perfil_usuario.foto = None
        perfil_usuario.save(update_fields=['foto', 'data_atualizacao'])

    return JsonResponse({
        'success': True,
        'mensagem': 'Foto removida com sucesso.'
    })


@login_required
@require_POST
def salvar_estabelecimento(request):
    perfil_usuario = obter_perfil(request.user)
    mercado = perfil_usuario.mercadinho

    nome = request.POST.get('nome', '').strip()
    telefone = request.POST.get('telefone', '').strip()
    email = request.POST.get('email', '').strip()
    cnpj = request.POST.get('cnpj', '').strip()
    localizacao = request.POST.get('localizacao', '').strip()

    if not nome:
        return JsonResponse(
            {'success': False, 'erro': 'Informe o nome do mercadinho.'},
            status=400
        )

    if mercado is None:
        mercado = Mercadinho.objects.create(
            nome=nome,
            telefone=telefone,
            email=email,
            cnpj=cnpj,
            localizacao=localizacao,
        )
        perfil_usuario.mercadinho = mercado
        perfil_usuario.save(update_fields=['mercadinho', 'data_atualizacao'])
    else:
        mercado.nome = nome
        mercado.telefone = telefone
        mercado.email = email
        mercado.cnpj = cnpj
        mercado.localizacao = localizacao
        mercado.save()

    return JsonResponse({
        'success': True,
        'mensagem': 'Dados do estabelecimento salvos com sucesso.',
        'mercado': dados_mercadinho(mercado),
    })

