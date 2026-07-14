from django.db import models


class Mercadinho(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=11)
    localizacao = models.CharField(max_length=100)
    email = models.EmailField()
    cnpj = models.CharField(max_length=18)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    cpf = models.CharField( max_length=14, unique=True)
    saldo_fiado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    limite_fiado = models.DecimalField( max_digits=10, decimal_places=2)
    ativo_fiado = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


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


    def __str__(self):
        return self.nome


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
