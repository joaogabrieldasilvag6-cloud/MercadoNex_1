from django.urls import path
from .views import estoque, registrar_entrada, ajustar_estoque, exportar_csv

urlpatterns = [
    path("", estoque, name="estoque"),
    path("registrar-entrada/", registrar_entrada, name="estoque_registrar_entrada"),
    path("ajustar/", ajustar_estoque, name="estoque_ajustar"),
    path("exportar/", exportar_csv, name="estoque_exportar"),
]
