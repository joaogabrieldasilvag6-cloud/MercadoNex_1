from django.contrib import admin

from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'prioridade', 'lida', 'criada_em')
    list_filter = ('tipo', 'lida', 'prioridade')
    search_fields = ('titulo', 'mensagem', 'usuario__username')
