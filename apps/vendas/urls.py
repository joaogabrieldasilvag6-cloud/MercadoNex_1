from django.urls import path
from .views import *

urlpatterns = [
    path("vendas/", vendas, name="vendas"),
    path("vendas/finalizar/", finalizar_venda, name="finalizar_venda"),

]