"""
URL configuration for Evara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('user/', include('UserAuth.urls')),
    path('shop/', include('Shop.urls')),
    path('account/', include('Account.urls')),
    path('adminpanel/', include('Adminauth.urls')),
    path('category/', include('Categories.urls')),
    path('product/',include('Products.urls')),
    path('cart/',include('Cart.urls')),
    path('checkout/',include('Order.urls')),
    path('coupon/',include('Coupon.urls')),
    path('wishlist/',include('Wishlist.urls')),
    path('messages/', include('messages_app.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
