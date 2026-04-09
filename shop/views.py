from django.shortcuts import render, get_object_or_404
from .models import Product, CartItem, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile
from django.core.mail import EmailMessage
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from .models import Category
@api_view(['GET'])
def api_categories(request):
    categories = Category.objects.all()

    data = []
    for c in categories:
        data.append({
            "id": c.id,
            "name": c.name
        })

    return Response(data)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        return Response({
            "message": "ok",
            "user_id": user.id
        })

    return Response({"error": "Invalid credentials"})


@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    address = request.data.get('address')

    if not username or not password:
        return Response({"error": "Missing fields"})

    if User.objects.filter(username=username).exists():
        return Response({"error": "User exists"})

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    # 🔥 OVO TI FALI
    UserProfile.objects.create(
        user=user,
        address=address
    )

    return Response({
        "message": "User created",
        "user_id": user.id
    })

# =========================
# 📦 PRODUCTS API
# =========================
@api_view(['GET'])
def api_products(request):
    category_id = request.GET.get('category_id')

    products = Product.objects.filter(available=True)

    if category_id:
        products = products.filter(category_id=category_id)

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "image": request.build_absolute_uri(p.image.url) if p.image else None
        })

    return Response(data)


# =========================
# 🛒 ADD TO CART
# =========================
@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')

    item, created = CartItem.objects.get_or_create(
        user_id=user_id,
        product_id=product_id
    )

    if not created:
        item.quantity += 1
        item.save()

    return Response({"message": "added"})


# =========================
# 🛒 GET CART
# =========================
@api_view(['GET'])
def get_cart(request):
    user_id = request.GET.get('user_id')

    items = CartItem.objects.filter(user_id=user_id)

    data = []
    total = 0

    for item in items:
        subtotal = float(item.product.price) * item.quantity
        total += subtotal

        data.append({
            "id": item.id,
            "name": item.product.name,
            "price": str(item.product.price),
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return Response({
        "items": data,
        "total": total
    })


def generate_pdf(order, items):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []

    # 🔷 HEADER
    elements.append(Paragraph("MYSHOP", styles['Title']))
    elements.append(Paragraph(f"INVOICE #{order.id}", styles['Heading2']))
    elements.append(Spacer(1, 15))

    # 👤 CUSTOMER
    elements.append(Paragraph(f"<b>Customer:</b> {order.user.first_name} {order.user.last_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Address:</b> {order.address}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # 📦 TABLE
    data = [["Product", "Qty", "Price (€)", "Total (€)"]]

    for item in items:
        total = float(item.price) * item.quantity
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price}",
            f"{total}"
        ])

    # 💰 TOTAL ROW
    data.append(["", "", "TOTAL", f"{order.total} €"])

    table = Table(data, colWidths=[150, 50, 80, 80])

    table.setStyle(TableStyle([
        # HEADER STYLE
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        # GRID
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        # TOTAL ROW
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # ALIGNMENT
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # 🧾 FOOTER
    elements.append(Paragraph("Thank you for your purchase!", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    return buffer

# =========================
# ➖ REMOVE FROM CART
# =========================
@api_view(['POST'])
def remove_from_cart(request):
    item_id = request.data.get('item_id')
    CartItem.objects.filter(id=item_id).delete()
    return Response({"message": "removed"})


# =========================
# 🧹 CLEAR CART
# =========================
@api_view(['POST'])
def clear_cart(request):
    CartItem.objects.all().delete()
    return Response({"message": "cart cleared"})


# =========================
# 🌐 WEB VIEWS (ako koristiš)
# =========================
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    return render(request, 'shop/product/detail.html', {
        'product': product
    })

@api_view(['POST'])
def checkout(request):
    user_id = request.data.get('user_id')

    items = CartItem.objects.filter(user_id=user_id)

    if not items:
        return Response({"error": "Cart empty"})

    total = 0
    for item in items:
        total += float(item.product.price) * item.quantity

    user = User.objects.get(id=user_id)

    # ✅ address fix
    try:
        profile = UserProfile.objects.get(user=user)
        address = profile.address
    except:
        address = "Nema adrese"

    # ✅ order mora biti prije emaila
    order = Order.objects.create(
        user=user,
        total=total,
        address=address
    )

    # ✅ items u order
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity
        )

    # 🧹 clear cart
    items.delete()

    # =========================
    # 📧 EMAIL + PDF
    # =========================
    try:
        print("SALJEM EMAIL NA:", user.email)

        order_items = OrderItem.objects.filter(order=order)

        pdf_buffer = generate_pdf(order, order_items)

        email = EmailMessage(
            subject="Račun - MyShop",
            body=f"""
            Hello {user.first_name},

            Thank you for your purchase!

            Order ID: {order.id}
            Total: {order.total} €

            Your invoice is attached.

            Best regards,
            MyShop
            """,
            from_email="tvojemail@gmail.com",
            to=[user.email],
        )

        email.attach(
            f"racun_{order.id}.pdf",
            pdf_buffer.getvalue(),  # 🔥 BITNO
            "application/pdf"
        )

        email.send()
        print("EMAIL POSLAN ✔")

    except Exception as e:
        print("❌ EMAIL ERROR:", e)

    # ✅ OBAVEZNO NA KRAJU
    return Response({
        "message": "Order created",
        "order_id": order.id
    })

@api_view(['GET'])
def user_orders(request):
    user_id = request.GET.get('user_id')

    orders = Order.objects.filter(user_id=user_id)

    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "total": str(o.total),
            "created": o.created.strftime("%Y-%m-%d %H:%M")
        })

    return Response(data)

@api_view(['POST'])
def update_quantity(request):
    item_id = request.data.get('item_id')
    action = request.data.get('action')  # "plus" ili "minus"

    item = CartItem.objects.get(id=item_id)

    if action == "plus":
        item.quantity += 1
    elif action == "minus":
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            return Response({"message": "removed"})

    item.save()
    return Response({"message": "updated"})