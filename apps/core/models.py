from django.db import models


class Mercadinho(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=11)
    localizacao = models.CharField(max_length=100)
    email = models.EmailField()
    cnpj = models.CharField(max_length=18)

    def __str__(self):
        return self.nome

