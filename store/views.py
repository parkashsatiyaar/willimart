from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import html
from django.utils.html import strip_tags
from django.conf import settings
from .models import Category, Customer, Product, Order
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Profile
import random
import razorpay
# Create your views here.


def Index(request):
    if request.method == "POST":
        product = request.POST.get('product_id')
        remove = request.POST.get('product_remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity+-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
        return redirect('home')
    else:
        categories = Category.getCategory()
        category_id = request.GET.get('category')
        if category_id:
            products = Product.getAllProductsByCategory(category_id)
        else:
            products = Product.getAllProducts()
        data = {'products': products, 'categories': categories}
        return render(request, "index.html", data)


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            if Customer.objects.filter(email=email).exists():
                messages.info(request, 'Email Already exist')
                return redirect('signup')
            elif Customer.objects.filter(phone=phone).exists():
                messages.info(request, 'Phone No Already exist')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already exist')
                return redirect('signup')
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password
            request.session['fname'] = fname
            request.session['lname'] = lname
            request.session['phone'] = phone
            otp = []
            num = str(random.randint(1000, 9999))
            for x in num:
                otp.append(x)
            context = {'name': username, 'auth_otp': otp}
            html_content = render_to_string(
                'pages/email.html', context)
            text_content = strip_tags(html_content)

            send_mail = EmailMultiAlternatives(
                "Account email verification",
                text_content,
                settings.EMAIL_HOST_USER,
                [email]
            )
            send_mail.attach_alternative(html_content, 'text/html')
            send_mail.send()
            profile = Profile(
                user=email, auth_otp=num)
            profile.save()
            return redirect('verify')
    categories = Category.getCategory()
    data = {'categories': categories}
    return render(request, "pages/signup.html", data)


# verify route


def verify(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            count = Profile.objects.filter(
                user=request.session['email']).count()
            profile = Profile.objects.filter(
                user=request.session['email'])
            if request.POST.get('auth_otp') == profile.values('auth_otp')[count-1]['auth_otp']:
                user = User.objects.create_user(
                    username=request.session['username'], password=request.session['password'], email=request.session['email'])
                user.save()
                customer = Customer(first_name=request.session['fname'], last_name=request.session['lname'],
                                    phone=request.session['phone'], email=request.session['email'], user=user)
                customer.register()
                auth.login(request, user)
                profile.delete()
                context = {'name': request.session['username']}
                html_content = render_to_string(
                    'pages/confirm_email.html', context)
                text_content = strip_tags(html_content)

                send_mail = EmailMultiAlternatives(
                    "Registration Successfull",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [request.session['email']]
                )
                send_mail.attach_alternative(html_content, 'text/html')
                send_mail.send()
                return redirect('home')
            profile.delete()
            messages.info(request, "Invalid otp or email register again!")
            return redirect('signup')
    return render(request, 'pages/verify.html')


def signin(request):
    if not request.session.get('next_url'):
        request.session['next_url'] = request.GET.get('next')
    url = request.session.get('next_url')
    if not request.session.get('cart'):
        request.session['cart'] = {}

    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                if url == "/checkout":
                    return redirect('cart')
                elif url:
                    return HttpResponseRedirect(url)
                else:
                    return redirect('home')
            else:
                messages.info(request, "Invalid Username or Password")
                return redirect('signin')
    categories = Category.getCategory()
    data = {'categories': categories}
    return render(request, "pages/signin.html", data)


# def signin(request):
#     categories = Category.getCategory()
#     data = {'categories': categories}
#     return render(request, "pages/signin.html", data)

@login_required(login_url='signin')
def signout(request):
    auth.logout(request)
    return redirect('signin')


def cart(request):
    if not request.session.get('cart'):
        request.session['cart'] = {}

    if request.method == "POST":
        product = request.POST.get('remove')
        cart = request.session.get('cart')
        cart.pop(product)
        request.session['cart'] = cart
        return redirect('cart')

    else:
        if not request.session.get('cart'):
            request.session['cart'] = {}
        categories = Category.getCategory()
        cart = list(request.session.get('cart'))
        products = Product.getAllProductsById(cart)
        data = {'categories': categories, 'products': products}
        return render(request, "pages/cart.html", data)


@login_required(login_url="signin")
def order(request):
    if not request.session.get('cart'):
        request.session['cart'] = {}
    orders = reversed(Order.objects.filter(customer=request.user.email))
    categories = Category.getCategory()
    data = {'categories': categories, 'orders': orders}
    return render(request, "orders/order.html", data)


def product(request, id):
    if request.method == "POST":
        product = request.POST.get('product_id')
        remove = request.POST.get('product_remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity+-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
        return HttpResponseRedirect(f"/product/{id}")
    else:
        if not request.session.get('cart'):
            request.session['cart'] = {}
        categories = Category.getCategory()
        products = Product.getProductById(id)
        data = {'products': products, 'categories': categories}
        return render(request, "pages/product.html", data)


@login_required(login_url='signin')
def checkout(request):

    if request.method == "POST":

        address = request.POST.get('address')
        phone = request.POST.get('phone')
        cart = request.session.get('cart')
        products = Product.getAllProductsById(list(cart))
        order_amount = 0
        for product in products:
            order_amount += product.price*int(cart.get(str(product.id)))*100
        order_currency = 'INR'
        order_receipt = "mynameisparkashsatiyaar"
        notes = {'Shipping address': address,
                 'client': request.user.email, 'product': product.name}
        client = razorpay.Client(
            auth=("rzp_test_FAXhzStIqvyJsh", "SaPnyZBpKrisAirIwpsMXMiz"))
        payment = client.order.create(
            dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
        print(payment)
        request.session['payment_id'] = payment['id']
        for product in products:
            order = Order(product=product, customer=request.user.email, price=product.price*int(cart.get(str(product.id))),
                          quantity=cart.get(str(product.id)), address=address, phone=phone, payment_id=payment['id'])
            order.save()
            print(product.price*int(cart.get(str(product.id))))
        data = {'payment': payment, 'products': products}
        return render(request, "pages/payment.html", data)
    request.session['cart'] = {}
    return redirect('order')


@login_required(login_url='signin')
def status(request):
    payment_process = {
        'razorpay_payment_id': request.GET.get('razorpay_payment_id'),
        'razorpay_order_id': request.GET.get('razorpay_order_id'),
        'razorpay_signature': request.GET.get('razorpay_signature')

    }

    client = razorpay.Client(
        auth=("rzp_test_FAXhzStIqvyJsh", "SaPnyZBpKrisAirIwpsMXMiz"))
    try:
        client.utility.verify_payment_signature(payment_process)
        orders = Order.objects.filter(
            payment_id=request.session.get('payment_id'))
        for order in orders:
            order.status = True
            order.save()
        request.session['cart'] = {}
    except:
        return redirect('order')
    return redirect('order')


@login_required(login_url='signin')
def account(request):
    customer = Customer.objects.filter(email=request.user.email)
    accounts = User.objects.filter(email=request.user.email)
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        for account_id in accounts:
            for account in customer:
                account.first_name = fname
                account.last_name = lname
                account.email = email
                account.phone = phone
                account_id.first_name = fname
                account_id.last_name = lname
                account_id.email = email
                account_id.phone = phone
                account_id.set_password(password)
                account.save()
                account_id.save()
        redirect('account')
    categories = Category.getCategory()
    data = {'accounts': customer, 'categories': categories}
    return render(request, 'pages/account.html', data)


def purchase(request):
    if request.method == "POST":
        product = request.POST.get('product_id')
        remove = request.POST.get('product_remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity+-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
    return redirect('cart')


def delete(request):
    if request.method == 'POST':
        account = User.objects.filter(email=request.user.email)
        account.delete()
    return redirect('home')
