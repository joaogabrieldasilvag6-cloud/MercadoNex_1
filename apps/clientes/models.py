from django.db import models

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


