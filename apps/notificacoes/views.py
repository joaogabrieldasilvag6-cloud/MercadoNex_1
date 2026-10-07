from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.clientes.models import Cliente
from apps.financeiro.models import Movimentacao
from apps.produtos.models import Produto
from .models import Notificacao


def _adicionar(lista, chave, tipo, titulo, mensagem, url, prioridade):
    lista.append({
        'chave': chave,
        'tipo': tipo,
        'titulo': titulo,
        'mensagem': mensagem,
        'url': url,
        'prioridade': prioridade,
    })


def _gerar_notificacoes():
    hoje = timezone.localdate()
    limite_validade = hoje + timedelta(days=7)
    itens = []

    produtos = Produto.objects.filter(status=True).order_by('quantidade', 'nome')
    for produto in produtos.filter(quantidade=0)[:10]:
        _adicionar(
            itens,
            f'estoque-falta-{produto.pk}',
            Notificacao.Tipo.ESTOQUE,
            'Produto sem estoque',
            f'{produto.nome} está sem estoque disponível.',
            '/estoque/',
            3,
        )

    for produto in produtos.filter(quantidade__gt=0, quantidade__lte=10)[:10]:
        _adicionar(
            itens,
            f'estoque-baixo-{produto.pk}',
            Notificacao.Tipo.ESTOQUE,
            'Estoque baixo',
            f'{produto.nome} está com apenas {produto.quantidade} unidade(s).',
            '/estoque/',
            2,
        )

    for produto in produtos.filter(validade__isnull=False, validade__gte=hoje, validade__lte=limite_validade).order_by('validade')[:10]:
        dias = (produto.validade - hoje).days
        texto = 'vence hoje' if dias == 0 else f'vence em {dias} dia(s)'
        _adicionar(
            itens,
            f'validade-{produto.pk}-{produto.validade.isoformat()}',
            Notificacao.Tipo.VALIDADE,
            'Produto próximo do vencimento',
            f'{produto.nome} {texto}.',
            '/estoque/',
            2 if dias <= 3 else 1,
        )

    for cliente in Cliente.objects.filter(saldo_fiado__gt=Decimal('0.00')).order_by('-saldo_fiado', 'nome')[:10]:
        _adicionar(
            itens,
            f'fiado-{cliente.pk}-{cliente.saldo_fiado}',
            Notificacao.Tipo.FIADO,
            'Fiado em aberto',
            f'{cliente.nome} possui R$ {cliente.saldo_fiado:.2f} em aberto.',
            '/clientes/',
            1,
        )

    financeiras = Movimentacao.objects.all()
    for movimento in financeiras.filter(status=Movimentacao.Status.ATRASADA).order_by('-data', '-id')[:10]:
        _adicionar(
            itens,
            f'financeiro-atrasada-{movimento.pk}',
            Notificacao.Tipo.FINANCEIRO,
            'Movimentação financeira atrasada',
            f'{movimento.descricao}: R$ {movimento.valor:.2f} está atrasado.',
            '/financeiro/',
            3,
        )

    for movimento in financeiras.filter(
        status=Movimentacao.Status.A_VENCER,
        data_vencimento__isnull=False,
        data_vencimento__gte=hoje,
        data_vencimento__lte=hoje + timedelta(days=3),
    ).order_by('data_vencimento', 'id')[:10]:
        dias = (movimento.data_vencimento - hoje).days
        texto = 'vence hoje' if dias == 0 else f'vence em {dias} dia(s)'
        _adicionar(
            itens,
            f'financeiro-vencer-{movimento.pk}-{movimento.data_vencimento.isoformat()}',
            Notificacao.Tipo.FINANCEIRO,
            'Conta próxima do vencimento',
            f'{movimento.descricao}: R$ {movimento.valor:.2f} {texto}.',
            '/financeiro/',
            2 if dias <= 1 else 1,
        )

    return itens


def _sincronizar(usuario):
    candidatos = _gerar_notificacoes()
    chaves = {item['chave'] for item in candidatos}

    with transaction.atomic():
        if chaves:
            Notificacao.objects.filter(usuario=usuario).exclude(chave__in=chaves).delete()
        else:
            Notificacao.objects.filter(usuario=usuario).delete()

        for item in candidatos:
            Notificacao.objects.update_or_create(
                usuario=usuario,
                chave=item['chave'],
                defaults={
                    'tipo': item['tipo'],
                    'titulo': item['titulo'],
                    'mensagem': item['mensagem'],
                    'url': item['url'],
                    'prioridade': item['prioridade'],
                },
            )

    return Notificacao.objects.filter(usuario=usuario)


@login_required
@require_POST
def marcar_lida(request, pk):
    notificacao = get_object_or_404(Notificacao, pk=pk, usuario=request.user)
    notificacao.lida = True
    notificacao.save(update_fields=['lida'])
    return JsonResponse({'sucesso': True})


@login_required
@require_POST
def marcar_todas_lidas(request):
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    return JsonResponse({'sucesso': True})


@login_required
def api_notificacoes(request):
    notificacoes = _sincronizar(request.user)
    limite = list(notificacoes.order_by('lida', '-prioridade', '-criada_em', '-id')[:20])
    return JsonResponse({
        'sucesso': True,
        'nao_lidas': notificacoes.filter(lida=False).count(),
        'notificacoes': [
            {
                'id': item.id,
                'tipo': item.tipo,
                'titulo': item.titulo,
                'mensagem': item.mensagem,
                'url': item.url,
                'prioridade': item.prioridade,
                'lida': item.lida,
                'criada_em': item.criada_em.strftime('%d/%m %H:%M'),
            }
            for item in limite
        ],
    })
