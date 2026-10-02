from django.urls import path
from .views import *    

urlpatterns = [
    path( "", configuracoes, name="configuracoes"),
    path( "salvar/", salvar_configuracoes, name="salvar_configuracoes"
    ),
]
