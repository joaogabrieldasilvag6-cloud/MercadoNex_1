from django.urls import path

from . views import *

urlpatterns = [
    path('', api_notificacoes, name='api_notificacoes'),
    path('<int:pk>/ler/', marcar_lida, name='marcar_lida'),
    path('ler-todas/', marcar_todas_lidas, name='marcar_todas_lidas'),
]
