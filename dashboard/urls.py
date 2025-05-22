from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),  
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),
    path('add-missing/', views.add_missing_person, name='add_missing'),
    path('match-person', views.match_missing_person, name='match_person'),
    path('success/', views.success_page, name='success'),
    path('logout/', views.logout_view, name='logout'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
