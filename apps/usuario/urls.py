from django.urls import path
from .views import * 


urlpatterns = [
    path('', perfil, name='perfil'),
    path('editar/', editar_perfil, name='editar_perfil'),
    path('senha/', alterar_senha, name='alterar_senha'),
    path('foto/', alterar_foto, name='alterar_foto'),
    path('foto/remover/', remover_foto, name='remover_foto'),
    path('estabelecimento/', salvar_estabelecimento, name='salvar_estabelecimento'),
]