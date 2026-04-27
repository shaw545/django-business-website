from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("products/", views.products, name="products"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),

    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),

    path("cart/", views.cart_view, name="cart"),
    path("cart-checkout/", views.cart_checkout, name="cart_checkout"),
    path("checkout/", views.checkout_view, name="checkout"),

    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("portfolio/", views.portfolio, name="portfolio"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),

    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("delete-product/<int:product_id>/", views.delete_product, name="delete_product"),
]