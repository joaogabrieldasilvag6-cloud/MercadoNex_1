from django.db import models
from django.conf import settings


class PerfilUsuario(models.Model):

    TIPOS = (('ADMINISTRADOR', 'Administrador'), ('GERENTE', 'Gerente'), ('OPERADOR', 'Operador'),)
    usuario = models.OneToOneField( settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='perfil_usuario' )
    nome_completo = models.CharField(max_length=150, blank=True)
    telefone = models.CharField(max_length=15, blank=True)
    tipo = models.CharField( max_length=20,choices=TIPOS, default='ADMINISTRADOR' )
    foto = models.ImageField( upload_to='usuarios/', blank=True, null=True)
    mercadinho = models.ForeignKey('core.Mercadinho',on_delete=models.SET_NULL, null=True,blank=True,related_name='usuarios')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuário'
        verbose_name_plural = 'Perfis de usuários'
        ordering = ['usuario__username']

    def __str__(self):
        return self.nome_completo or self.usuario.username
