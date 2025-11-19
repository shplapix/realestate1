from django.contrib import admin
from.models import Realtor  # <-- Импортируем вашу модель

# Эта строка "регистрирует" модель в админке
admin.site.register(Realtor)