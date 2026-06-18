from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Product, Order, OrderItem, SellerProfile
from .models import Product, ProductColor, ProductImage
from .models import Product, ProductReview
from django.db.models import Avg
from django.conf import settings
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI


# =========================
# PUBLIC PAGES
# =========================


def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["pending", "paid", "shipped", "delivered"]:
            order.status = new_status
            order.save()

    return redirect("seller_dashboard")

def home(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
       products = products.filter(category__iexact=category)

    categories = [
        "Electronics",
        "Fashion & Clothing",
        "Home & Living",
        "Beauty & Personal Care",
        "Sports",
        "Other",
    ]

    return render(request, "home.html", {
        "products": products,
        "query": query,
        "categories": categories,
        "selected_category": category,
    })
def products_view(request):
    query = request.GET.get("q", "")

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, "products.html", {
        "products": products,
        "query": query,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    average_rating = ProductReview.objects.filter(
        product__seller=product.seller
    ).aggregate(Avg("rating"))["rating__avg"]

    if average_rating:
       average_rating = round(average_rating, 1)
    return render(request, "product_detail.html", {
        "product": product,
        "average_rating": average_rating,
    })
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    size_options = []
    color_options = []

    if product.size:
        size_options = [s.strip() for s in product.size.split(",") if s.strip()]

    color_options = [
        c.color_name.strip()
        for c in product.colors.all()
        if c.color_name and c.color_name.strip()
    ]

    return render(request, "product_detail.html", {
        "product": product,
        "size_options": size_options,
        "color_options": color_options,
    })
# =========================
# CART
# =========================

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart = request.session.get("cart", {})

    # ADD THESE LINES HERE
    selected_size = request.POST.get("selected_size", "")
    selected_color = request.POST.get("selected_color", "")

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id]["quantity"] += 1
    else:
        cart[product_id] = {
            "name": product.name,
            "amount": str(product.amount),
            "quantity": 1,
            "selected_size": selected_size,
            "selected_color": selected_color,
        }

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")
def buy_now(request, product_id):
    request.session["cart"] = {str(product_id): 1}
    request.session.modified = True
    return redirect("checkout")
def cart_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        if isinstance(item, dict):
            quantity = int(item.get("quantity", 1))
            product.selected_color = item.get("color", item.get("selected_color", ""))
            product.selected_size = item.get("size", item.get("selected_size", ""))
        else:
            quantity = int(item)
            product.selected_color = ""
            product.selected_size = ""

        product.quantity = quantity
        product.subtotal = product.amount * quantity

        products.append(product)
        total += product.subtotal

    return render(request, "cart.html", {
        "products": products,
        "total": total,
    })
def increase_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def decrease_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def remove_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================
# CHECKOUT / ORDER
# =========================

from django.conf import settings
from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem


def checkout_view(request):
    cart = request.session.get("cart", {})
    print("CART DATA:", cart)
    products = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        if isinstance(item, dict):
            quantity = int(item.get("quantity", 1))
            product.selected_color = item.get("color", item.get("selected_color", ""))
            product.selected_size = item.get("size", item.get("selected_size", ""))
        else:
            quantity = int(item)
            product.selected_color = ""
            product.selected_size = ""
        product.quantity = quantity
        product.subtotal = product.amount * quantity
        products.append(product)
        total += product.subtotal

    if request.method == "POST":
        if not products:
            request.session["cart"] = {}
            return redirect("cart")

        order = Order.objects.create(
            buyer_name=request.POST.get("buyer_name"),
            buyer_phone=request.POST.get("buyer_phone"),
            buyer_email=request.POST.get("buyer_email"),
            buyer_address=request.POST.get("buyer_address"),     
            payment_method=request.POST.get("payment_method"),
            payment_proof=request.FILES.get("payment_proof"),
            total_amount=total,
        )

        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                quantity=product.quantity,
                price=product.amount,
                color=getattr(product, "selected_color", ""),
                size=getattr(product, "selected_size", ""),
                amount=product.amount,
                subtotal=product.subtotal,
            )

        request.session["cart"] = {}
        return redirect("order_confirmation")

    return render(request, "checkout.html", {
        "products": products,
        "total": total,
        "platform_orange_money": settings.PLATFORM_ORANGE_MONEY,
        "platform_africell_money": settings.PLATFORM_AFRICELL_MONEY,
    })
def order_confirmation(request):
    order_id = request.session.get("last_order_id")
    order = None

    if order_id:
        order = Order.objects.filter(id=order_id).first()

    return render(request, "order_confirmation.html", {
        "order": order
    })
# =========================
# AUTH
# =========================

def register(request):
    if request.method == "POST":
        seller_type = request.POST.get("seller_type")

        if seller_type == "business":
            username = request.POST.get("username_business")
        else:
            username = request.POST.get("username")

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email", "")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        if not username:
            messages.error(request, "Username is required")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another username.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        SellerProfile.objects.create(
            user=user,
            seller_type=seller_type,
            business_name=request.POST.get("business_name", ""),
            business_address=request.POST.get("business_address", ""),
            business_logo=request.FILES.get("business_logo"),
            phone=request.POST.get("phone", ""),
            
      )

        messages.success(request, "Seller account created successfully.")
        return redirect("login")

    return render(request, "register.html")

def logout_view(request):
    logout(request)
    return redirect("home")
# =========================
# SELLER DASHBOARD
# =========================

@login_required
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)
    order_items = OrderItem.objects.filter(seller=request.user).order_by("-order__created_at")

    total_orders = order_items.count()
    pending_orders = order_items.filter(order__status="pending").count()
    paid_orders = order_items.filter(order__status="paid").count()
    shipped_orders = order_items.filter(order__status="shipped").count()
    delivered_orders = order_items.filter(order__status="delivered").count()

    return render(request, "dashboard.html", {
        "products": products,
        "order_items": order_items,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
    })
def add_product(request):
    if request.method == "POST":
        product = Product.objects.create(
            seller=request.user,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            amount=request.POST.get("amount"),
            category=request.POST.get("category"),
            condition=request.POST.get("condition"),
            image=request.FILES.get("image"),
            image_2=request.FILES.get("image_2"),
            image_3=request.FILES.get("image_3"),
            image_4=request.FILES.get("image_4"),
            image_5=request.FILES.get("image_5"),
        )

        return redirect("seller_dashboard")

    return render(request, "add_product.html")       
     
            
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == "POST":
        product.name = request.POST.get("name") or product.name
        product.description = request.POST.get("description") or product.description
        product.amount = request.POST.get("amount") or product.amount
        product.category = request.POST.get("category") or product.category
        product.condition = request.POST.get("condition") or product.condition
        product.size = request.POST.get("size") or product.size

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("seller_dashboard")

    return render(request, "edit_product.html", {
        "product": product
    })
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user
    )

    if request.method == "POST":
        product.delete()
        return redirect("seller_dashboard")

    return render(request, "delete_product.html", {
        "product": product
    })


def seller_store(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    products = Product.objects.filter(seller=seller)

    ratings = ProductReview.objects.filter(seller=seller)
    average_rating = ratings.aggregate(Avg("rating"))["rating__avg"]

    if average_rating:
        average_rating = round(average_rating, 1)
    else:
        average_rating = "No ratings yet"

    return render(request, "seller_store.html", {
        "seller": seller,
        "products": products,
        "ratings": ratings,
        "average_rating": average_rating,
    })
# =========================
# STATIC PAGES
# =========================

@login_required
def submit_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect("products_view")

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        ProductReview.objects.create(
            product=product,
            seller=product.seller,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return redirect("product_detail", product_id=product.id)

    return redirect("product_detail", product_id=product.id)
def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")

@csrf_exempt
def chatbot_response(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request."})

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").lower()
    except:
        return JsonResponse({"reply": "Sorry, I did not understand that."})

    if "delivery" in user_message or "delivered" in user_message or "when will my order" in user_message:
        reply = "Orders are usually delivered within 1–3 business days in Freetown and 3–7 business days outside Freetown. Delivery time may depend on the seller location and item availability."

    elif "pay" in user_message or "payment" in user_message or "orange" in user_message or "afri" in user_message:
        reply = "You can pay using Orange Money or Afri Money. After payment, upload your proof of payment during checkout so the seller can verify it."

    elif "cart" in user_message:
        reply = "To view your cart, click the cart icon at the top of the page or the Cart button in the bottom menu on mobile."

    elif "seller" in user_message or "sell" in user_message or "register" in user_message:
        reply = "To become a seller, click Register or Become a Seller, complete your seller profile, agree to the terms and privacy policy, then start adding products."

    elif "order" in user_message or "status" in user_message or "track" in user_message:
        reply = "To check your order status, please contact the seller or check your order confirmation. Order status may show Pending, Paid, Shipped, or Delivered."
    elif (
    "refund" in user_message
    or "return" in user_message
    or "wrong item" in user_message
    or "damaged" in user_message
    or "broken" in user_message
):
    reply = (
        "I’m sorry about that. Online Luma can help you with returns and refunds. "
        "Please send the following details here:\n\n"
        "1. Order number\n"
        "2. Phone number\n"
        "3. Delivery address\n"
        "4. Product name\n"
        "5. Reason for refund or return\n\n"
        "After receiving these details, Online Luma support will review the issue with the seller and help with a replacement, return, or refund."
   )

   elif "hello" in user_message or "hi" in user_message:
      reply = "Hello! Welcome to Online Luma. I can help with orders, payment, delivery, seller registration, and shopping questions."    elif "support" in   user_message or "help" in user_message or "complaint" in user_message:
    reply = (
        "Online Luma support can help with orders, payments, returns, refunds, and seller issues. "
        "Please provide your order number, phone number, product name, and a short explanation of the issue."
    )
   elif "order" in user_message and "phone" in user_message and "address" in user_message:
       reply = (
        "Thank you for providing your order details. "
        "Your return/refund request has been received by Online Luma support. "
        "Our team will review the information and contact you about the next step."
      )
   else:
        reply = "I can help with Online Luma orders, delivery, payment, cart, seller registration, and product questions. Please ask your question again."

    return JsonResponse({"reply": reply})