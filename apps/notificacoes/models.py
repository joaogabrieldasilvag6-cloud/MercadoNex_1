from django.conf import settings
from django.db import models


class Notificacao(models.Model):
    class Tipo(models.TextChoices):
        ESTOQUE = 'estoque', 'Estoque'
        VALIDADE = 'validade', 'Validade'
        FIADO = 'fiado', 'Fiado'
        FINANCEIRO = 'financeiro', 'Financeiro'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes',
    )
    chave = models.CharField(max_length=180)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    titulo = models.CharField(max_length=120)
    mensagem = models.CharField(max_length=240)
    url = models.CharField(max_length=255, blank=True)
    prioridade = models.PositiveSmallIntegerField(default=1)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lida', '-prioridade', '-criada_em', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'chave'],
                name='uniq_notificacao_usuario_chave',
            )
        ]
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return self.titulo
