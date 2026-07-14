from django.contrib import admin
from .models import (Mercadinho, Cliente, Produto, Venda, ItemVenda, Estoque,)

admin.site.register(Mercadinho)
admin.site.register(Cliente)
admin.site.register(Produto)
admin.site.register(Venda)
admin.site.register(ItemVenda)
admin.site.register(Estoque)
