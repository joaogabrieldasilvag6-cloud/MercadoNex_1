from django.urls import path
from .views import *

urlpatterns = [
    path("", vendas, name="vendas"),
    path("finalizar/", finalizar_venda, name="finalizar_venda"),
    path("fiado/<int:venda_id>/quitar/", quitar_fiado, name="quitar_fiado"),

]