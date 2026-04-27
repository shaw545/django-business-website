from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    path("products/", views.products_view, name="products"),

    # Product
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),

    # Cart & Checkout
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),

    # Pages
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("portfolio/", views.portfolio, name="portfolio"),

    # Auth
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),

    # Dashboard (fix error)
    path("dashboard/", views.seller_dashboard, name="seller_dashboard"),
]