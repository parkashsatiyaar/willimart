from django.urls import path
from . import views
from django.views.generic import RedirectView
urlpatterns = [
    path('', views.Index, name="home"),
    path('signin', views.signin, name="signin"),
    path('signup', views.signup, name="signup"),
    path('signout', views.signout, name="signout"),
    path('cart', views.cart, name="cart"),
    path('order', views.order, name="order"),
    path('checkout', views.checkout, name="checkout"),
    path('product', RedirectView.as_view(url='signin')),
    path('product/<int:id>', views.product, name="product"),
    path('account', views.account, name="account"),
    path('purchase', views.purchase, name="purchase"),
    path('delete', views.delete, name="delete"),
]
