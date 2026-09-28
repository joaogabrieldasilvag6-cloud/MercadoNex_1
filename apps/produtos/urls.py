from django.urls import path
from .views import *

urlpatterns = [
    path("", produtos, name="produtos"),
    path('cadastrar/', cadastrar_produto, name='cadastrar_produto'),
    path("excluir/<int:id>/", excluir_produto,name="excluir_produto"),
    path("editar/<int:id>/", editar_produto, name="editar_produto"),
    path("json/<int:id>/", produto_json, name="produto_json" ),

]