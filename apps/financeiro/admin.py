from django.contrib import admin
from .models import Movimentacao


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "tipo",
        "valor",
        "categoria",
        "data",
        "status",
        "forma_pagamento",
    )
    list_filter = ("tipo", "status", "categoria", "forma_pagamento")
    search_fields = ("descricao", "referencia", "observacao")
    date_hierarchy = "data"
