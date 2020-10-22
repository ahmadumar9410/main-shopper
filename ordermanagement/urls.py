from django.urls import path
from ordermanagement import views

urlpatterns = [
    path('', views.index),
    path('shop/', views.shop),
    path('search/', views.search),
    path('favourite/<slug>/', views.favourite),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('product/<slug>/', views.product),
    path('remove/<slug>/', views.remove),
    path('cart/', views.cart),
    path('checkout/', views.checkout),
    path('thankyou/', views.thankyou),
]