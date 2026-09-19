from django.urls import path
from .views import *

urlpatterns = [

    path("clientes/", clientes, name="clientes"),
    path("clientes/cadastrar/", cadastrar_cliente, name="cadastrar_cliente"),
    path("clientes/excluir/<int:id>/", excluir_cliente, name="excluir_cliente"),
    path("clientes/editar/<int:id>/", editar_cliente, name="editar_cliente"),
    path("clientes/json/<int:id>/", cliente_json, name="cliente_json"),

]