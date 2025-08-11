"""A2SL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/',views.about_view,name='about'),
    path('contact/',views.contact_view,name='contact'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('signup/',views.signup_view,name='signup'),
    path('animation/',views.animation_view,name='animation'),
    path('',views.home_view,name='home'),
    path('sign-language/', views.sign_language_home, name='sign_language_home'),
    path('sign-language/video_feed/', views.get_video_feed, name='video_feed'),
    path('sign-language/clear_text/', views.clear_text, name='clear_text'),
    path('sign-language/select_suggestion/', views.select_suggestion, name='select_suggestion'),
    # ... your existing paths ...
   # path('second-model/', views.second_model_view, name='second_model'),
    path('', views.landing_page, name='landing'),
    path('text-to-sign/', views.text_to_sign, name='text_to_sign'),  # Add this line
    path('sign-to-text/', views.sign_to_text, name='sign_to_text'),  # Add this line

]


