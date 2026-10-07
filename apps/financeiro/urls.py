from django.urls import path

from . import views

app_name = "financeiro"

urlpatterns = [
    path("", views.financeiro, name="financeiro"),
    path("movimentacao/nova/", views.nova_movimentacao, name="nova_movimentacao"),
    path("movimentacao/<int:pk>/excluir/", views.excluir_movimentacao, name="excluir_movimentacao"),
    path("exportar/", views.exportar_csv, name="exportar_csv"),
    path("api/resumo/", views.api_resumo, name="api_resumo"),
]
