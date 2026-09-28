from django.urls import path
from .views import *


urlpatterns = [
    path("", clientes, name="clientes"),
    path("cadastrar/", cadastrar_cliente, name="cadastrar_cliente"),
    path("excluir/<int:id>/", excluir_cliente, name="excluir_cliente"),
    path("editar/<int:id>/", editar_cliente, name="editar_cliente"),
    path("json/<int:id>/", cliente_json, name="cliente_json"),
    path("fiado/<int:id>/quitar/", quitar_fiado_cliente, name="quitar_fiado_cliente"),
]