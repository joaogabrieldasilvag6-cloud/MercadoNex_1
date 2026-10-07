from django.urls import path
from . import views

urlpatterns = [
    path("", views.clientes, name="clientes"),
    path("cadastrar/", views.cadastrar_cliente, name="cadastrar_cliente"),
    path("excluir/<int:id>/", views.excluir_cliente, name="excluir_cliente"),
    path("editar/<int:id>/", views.editar_cliente, name="editar_cliente"),
    path("json/<int:id>/", views.cliente_json, name="cliente_json"),
    path("bloquear/<int:id>/", views.alternar_bloqueio_cliente, name="alternar_bloqueio_cliente"),
    path("fiado/<int:id>/quitar/", views.quitar_fiado_cliente, name="quitar_fiado_cliente"),
]
