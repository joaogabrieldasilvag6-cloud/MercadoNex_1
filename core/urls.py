from django.urls import path
from .views import *

urlpatterns = [
    path('', inicial, name='inicial'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('cadastro/', cadastro, name='cadastro'),
    path('dashboard/', dashboard, name='dashboard'),

    path("produtos/", produtos, name="produtos"),
    path('produtos/cadastrar/', cadastrar_produto, name='cadastrar_produto'),
    path("produtos/excluir/<int:id>/", excluir_produto,name="excluir_produto"),
    path("produtos/editar/<int:id>/", editar_produto, name="editar_produto"),
    path("produtos/json/<int:id>/", produto_json, name="produto_json" ),

    path("clientes/cadastrar/", cadastrar_cliente, name="cadastrar_cliente"),
    path("clientes/excluir/<int:id>/", excluir_cliente, name="excluir_cliente"),
    path("clientes/editar/<int:id>/", editar_cliente, name="editar_cliente"),
    path("clientes/json/<int:id>/", cliente_json, name="cliente_json"),

    path("vendas/", vendas, name="vendas"),
    path("vendas/finalizar/", finalizar_venda, name="finalizar_venda"),

]