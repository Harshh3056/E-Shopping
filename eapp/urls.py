from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('admin/',admin.site.urls),
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('profile',views.profile,name='profile'),
    path('logout',views.logout,name='logout'),
    path('forget',views.forget,name='forget'),
    path('confirm_password',views.confirm_password,name='confirm_password'),
    path('shop',views.shop,name='shop'),
    path('shop/<str:subcategory_name>/', views.shop, name='shop_by_subcategory'),
    path('cart',views.cart,name='cart'),
    path('contact',views.contact,name='contact'),
    path('detail',views.detail,name='detail'),
    path('add_to_wishlist/<int:id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('rem_wishlist/<int:id>', views.rem_wishlist, name='rem_wishlist'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('incr/<int:id>/', views.incr, name='incr'),
    path('decr/<int:id>/', views.decr, name='decr'),
    path('rem/<int:id>/', views.rem, name='rem'),
    path('detail1/<int:id>', views.detail1, name='detail1'),
    path('checkout',views.checkout,name='checkout'),
    path('order',views.order,name='order'),
    path('cancel_order/<int:id>/',views.cancel_order,name='cancel_order'),
    path('shop/<str:subcategory_name>/', views.shop, name='shop_by_subcategory'),
]