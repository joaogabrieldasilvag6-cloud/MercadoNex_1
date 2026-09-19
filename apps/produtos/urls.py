from django.urls import path
from .views import *

urlpatterns = [
    path("produtos/", produtos, name="produtos"),
    path('produtos/cadastrar/', cadastrar_produto, name='cadastrar_produto'),
    path("produtos/excluir/<int:id>/", excluir_produto,name="excluir_produto"),
    path("produtos/editar/<int:id>/", editar_produto, name="editar_produto"),
    path("produtos/json/<int:id>/", produto_json, name="produto_json" ),

]