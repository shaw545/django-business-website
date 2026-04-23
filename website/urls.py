from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("portfolio/", views.portfolio, name="portfolio"),

    path("products/", views.products, name="products"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/<int:product_id>/add-to-cart/", views.add_to_cart, name="add_to_cart"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/update/<int:index>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:index>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/<int:product_id>/", views.checkout, name="checkout"),
    path("cart/checkout/", views.cart_checkout, name="cart_checkout"),

    path("contact/", views.contact, name="contact"),

    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", views.seller_logout, name="logout"),

    path("seller/dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/add-product/", views.add_product, name="add_product"),
    path("seller/edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("seller/delete-product/<int:product_id>/", views.delete_product, name="delete_product"),
    path("seller/delete-gallery-image/<int:image_id>/", views.delete_gallery_image, name="delete_gallery_image"),
    path("seller/withdraw/", views.request_withdrawal, name="request_withdrawal"),
]