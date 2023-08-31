from django.contrib.auth import views as auth_views
from . import views
from .views import upload_image
from django.contrib import admin
from django.urls import path, include

from .views import AdListView, AdDetailView

app_name = 'mmorpg'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signup/done/', views.signup_done, name='signup_done'),
    path('confirm-email/<str:code>/', views.confirm_email, name='confirm_email'),
    path('login/', auth_views.LoginView.as_view(template_name='board/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='board/logout.html'), name='logout'),
    path('board/advertisements/', views.AdvertisementListView.as_view(), name='advertisement_list'),
    path('board/advertisements/create/', views.AdvertisementCreateView.as_view(), name='advertisement_create'),
    path('board/advertisements/<int:pk>/edit/', views.AdvertisementUpdateView.as_view(), name='advertisement_update'),
    path('board/advertisements/<int:pk>/delete/', views.AdvertisementDeleteView.as_view(), name='advertisement_delete'),
    path('board/advertisements/<int:advertisement_id>/responses/create/', views.response_create, name='response_create'),
    path('board/advertisements/<int:advertisement_id>/responses/', views.ResponseListView.as_view(), name='response_list'),
    path('board/responses/<int:response_id>/delete/', views.response_delete, name='response_delete'),
    path('board/responses/<int:response_id>/accept/', views.response_accept, name='response_accept'),
    path('board/newsletter/create/', views.newsletter_create, name='newsletter_create'),
    path('board/newsletters/', views.NewsletterListView.as_view(), name='newsletter_list'),
    path('board/newsletters/<int:newsletter_id>/subscribe/', views.subscribe, name='subscribe'),
    path('board/newsletters/<int:newsletter_id>/unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('upload_image/', upload_image, name='upload_image'),
    path('admin/', admin.site.urls),
    path('mmorpg/', include('mmorpg.urls')),
    path('', AdListView.as_view(), name='ad_list'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
]
