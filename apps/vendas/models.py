from django.db import models
from apps.clientes.models import Cliente
from apps.produtos.models import Produto

class Venda(models.Model):

    STATUS = [("ABERTA", "Aberta"), ("FINALIZADA", "Finalizada"), ("CANCELADA", "Cancelada"),]
    FORMA_PAGAMENTO = [  ("DINHEIRO", "Dinheiro"),  ("PIX", "Pix"),  ("CARTAO", "Cartão"),  ("FIADO", "Fiado"),]
    cliente = models.ForeignKey( Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="vendas" )
    data = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default="ABERTA" )
    forma_pagamento = models.CharField( max_length=20, choices=FORMA_PAGAMENTO, blank=True)
    total = models.DecimalField( max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField( max_digits=10, decimal_places=2, default=0)
    valor_final = models.DecimalField( max_digits=10,decimal_places=2, default=0)

    def __str__(self):
        return f"Venda #{self.id}"


class ItemVenda(models.Model):

    venda = models.ForeignKey( Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey( Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField( max_digits=10,decimal_places=2)
    subtotal = models.DecimalField( max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade})"
