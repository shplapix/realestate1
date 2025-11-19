"""
URL configuration for realestate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Путь к админ-панели
    path('admin/', admin.site.urls), 
    
    # 2. Пути для приложения listings ( /listings/ и /listings/1/ )
    path('listings/', include('listings.urls')), # [1]
    
    # 3. Пути для приложения pages ( / и /about/ )
    # Этот путь должен быть последним, так как '' "поймает" все
    path('chat/', include('chat.urls')),
    path('', include('pages.urls')),   
]

# Этот блок, который у вас уже есть, нужен для 
# отображения загруженных ФОТО в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # [2, 3]