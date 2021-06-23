from django.shortcuts import redirect, render
from .models import Category, Customer, Product, Order
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
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
            user = User.objects.create_user(
                username=username, password=password, email=email)
            user.save()
            customer = Customer(first_name=fname, last_name=lname,
                                phone=phone, email=email, user=user)
            customer.register()
            auth.login(request, user)
            return redirect('home')
    categories = Category.getCategory()
    data = {'categories': categories}

    return render(request, "pages/signup.html", data)


def signin(request):
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
    products = reversed(Order.objects.filter(customer=request.user.email))
    categories = Category.getCategory()
    data = {'categories': categories, 'products': products}
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
        for product in products:
            order = Order(product=product, customer=request.user.email, price=product.price,
                          quantity=cart.get(str(product.id)), address=address, phone=phone)
            order.save()
        request.session['cart'] = {}

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