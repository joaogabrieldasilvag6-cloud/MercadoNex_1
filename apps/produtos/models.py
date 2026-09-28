from django.db import models
from apps.core.models import Mercadinho

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)
    codigo = models.CharField(max_length=30, unique=True)
    marca = models.CharField(max_length=50, blank=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField( max_digits=10, decimal_places=2, null=True, blank=True )
    quantidade = models.PositiveIntegerField(default=0)
    validade = models.DateField(null=True, blank=True)
    fornecedor = models.CharField(max_length=100, blank=True)
    status = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)


    def __str__(self):
        return self.nome






class Estoque(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE
    )

    mercadinho = models.ForeignKey(
        Mercadinho,
        on_delete=models.CASCADE
    )

    categoria = models.CharField(max_length=50)
    validade = models.DateField()
    fornecedor = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    data_entrada = models.DateField()

    def __str__(self):
        return self.produto.nome

