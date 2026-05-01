from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("", views.home, name="home"),
    path("products/", views.products_view, name="products"),

    path("dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("dashboard/add-product/", views.add_product, name="add_product"),
    path("dashboard/edit-product/<int:product_id>/", views.edit_product, name="edit_product"),

    path("product/<int:product_id>/", views.product_detail, name="product_detail"),

    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("products/", views.products_view, name="products"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),

    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("dashboard/delete-product/<int:product_id>/", views.delete_product, name="delete_product"),
    path("cart/increase/<int:product_id>/", views.increase_cart_item, name="increase_cart_item"),
    path("cart/decrease/<int:product_id>/", views.decrease_cart_item, name="decrease_cart_item"),
    path("cart/remove/<int:product_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("order-confirmation/", views.order_confirmation, name="order_confirmation"),
]