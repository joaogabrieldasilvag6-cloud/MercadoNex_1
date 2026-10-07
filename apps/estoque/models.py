from django.conf import settings
from django.db import models

from apps.produtos.models import Produto


class MovimentacaoEstoque(models.Model):
    TIPOS = (
        ("entrada", "Entrada"),
        ("saida", "Saída"),
        ("ajuste", "Ajuste"),
    )

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="movimentacoes_estoque")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.PositiveIntegerField(default=0)
    estoque_anterior = models.PositiveIntegerField(default=0)
    estoque_novo = models.PositiveIntegerField(default=0)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    observacao = models.CharField(max_length=200, blank=True)
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_movimentacao", "-id"]
        verbose_name = "Movimentação de estoque"
        verbose_name_plural = "Movimentações de estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome}"
