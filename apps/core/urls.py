from django.urls import path
from .views import *

urlpatterns = [
    path('', inicial, name='inicial'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('cadastro/', cadastro, name='cadastro'),
    path('dashboard/', dashboard, name='dashboard'),

 

]