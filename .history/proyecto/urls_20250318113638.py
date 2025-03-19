"""
URL configuration for proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from casaKolor1 import views

from django.contrib.auth import views as auth_views
from casaKolor1.views import enviar_sugerencia
from django.shortcuts import render
from casaKolor1.views import login_view, clear_login_success,perfil




urlpatterns = [
    path('admin/', admin.site.urls),
    path('' ,views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('productos/',views.productos_view, name='productos'),
    # path('sugerencias',views.sugerencias, name='sugerencias'),
    path('herramientas/', views.lista_herramientas, name='herramientas'),
    path('pinturas/', views.lista_pinturas, name='pinturas'),
    path('mision', views.mision, name='mision'),
    # path('sugerencias/', views.sugerencia_view, name='sugerencias'),
    # path('sugerencia-exitosa/', views.sugerencia_exitosa, name='sugerencia_exitosa'),
    path('buscar/', views.buscar, name='buscar'),

    #login
    path('sugerencias/', enviar_sugerencia, name='sugerencias'),
    path('sugerencia_exitosa/', lambda request: render(request, 'sugerencia_exitosa.html'), name='sugerencia_exitosa'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    #recuperar contraseña
    path('restablecer/', views.restablecer, name='restablecer'),
    path('cambiar-contraseña/<str:uidb64>/<str:token>/', views.cambiar_contraseña, name='cambiar_contraseña'),
    path('confirmacion/', views.confirmacion, name='confirmacion'),
    path('carrito/', views.carrito, name='carrito'),
    path('pasarela-pago/', views.pasarela_pago, name='pasarela_pago'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),

    #mensaje de alerta
    path('clear-login-success/', clear_login_success, name='clear_login_success'),

    path('perfil/', perfil, name='perfil'),
    path('manual'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
