from django.db import models
from decimal import Decimal


class Movimentacao(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saída"

    class Status(models.TextChoices):
        PAGA = "PAGA", "Paga"
        A_VENCER = "A_VENCER", "A vencer"
        ATRASADA = "ATRASADA", "Atrasada"

    mercadinho = models.ForeignKey( "core.Mercadinho", on_delete=models.CASCADE,related_name="movimentacoes_financeiras",null=True,blank=True,)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    descricao = models.CharField(max_length=150)
    categoria = models.CharField(max_length=80, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    data = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)

    forma_pagamento = models.CharField(max_length=40, blank=True)
    status = models.CharField( max_length=12, choices=Status.choices, default=Status.PAGA,)
    referencia = models.CharField(max_length=100, blank=True)
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "Movimentação financeira"
        verbose_name_plural = "Movimentações financeiras"

    def __str__(self):
        sinal = "+" if self.tipo == self.Tipo.ENTRADA else "-"
        return f"{sinal} R$ {self.valor:.2f} — {self.descricao}"

    @property
    def valor_assinado(self):
        return self.valor if self.tipo == self.Tipo.ENTRADA else -self.valor

