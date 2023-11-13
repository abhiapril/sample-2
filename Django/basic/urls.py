


from django.urls import path
from . import views

urlpatterns = [
    path('', views.Homepage, name="homepage"),
    path('about/', views.About, name="about"),
    path('contactus/', views.ContactUs, name="contactus"),
    path('recommend_hotels/', views.Recommend_hotels, name="recommend_hotels"),
    
]