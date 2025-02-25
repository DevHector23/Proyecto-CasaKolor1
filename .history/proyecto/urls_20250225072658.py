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




urlpatterns = [
    path('admin/', admin.site.urls),
    path('' ,views.home, name='home'),
    path('inicio',views.inicio, name='inicio'),
    # path('register/', views.register, name='register'),
    # path('login/', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('productos',views.productos_view, name='productos'),
    # path('sugerencias',views.sugerencias, name='sugerencias'),
    path('carrito', views.carrito, name='carrito'),
    path('herramientas/', views.lista_herramientas, name='herramientas'),
    path('pinturas/', views.lista_pinturas, name='pinturas'),
    path('mision', views.mision, name='mision'),
    path('sugerencias/', enviar_sugerencia, name='sugerencias'),
    path('sugerencia-exitosa/', views.sugerencia_exitosa, name='sugerencia_exitosa'),
    path('buscar/', views.buscar, name='buscar'),

    #login
   




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
