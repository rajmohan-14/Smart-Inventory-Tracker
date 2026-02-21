from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

path('accounts/logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]