from django.urls import path
from .views import *

urlpatterns = [
    path("", relatorios, name="relatorios"),
    path("exportar/vendas/", relatorios_exportar_vendas, name="relatorios_exportar_vendas"),
    path("exportar/produtos/", relatorios_exportar_produtos, name="relatorios_exportar_produtos"),
    path("exportar/estoque/", relatorios_exportar_estoque, name="relatorios_exportar_estoque"),
    path("exportar/clientes/", relatorios_exportar_clientes, name="relatorios_exportar_clientes"),

 

]