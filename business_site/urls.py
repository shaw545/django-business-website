from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👉 This line is MISSING in your project
    path('', include('website.urls')),
]