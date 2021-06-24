from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @staticmethod
    def getCategory():
        return Category.objects.all()


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="uploads/products/%Y/%m/%d/")

    def __str__(self):
        return self.name

    @staticmethod
    def getAllProducts():
        return Product.objects.all()

    @staticmethod
    def getAllProductsById(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def getProductById(id):
        return Product.objects.filter(id=id)

    @staticmethod
    def getAllProductsByCategory(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.objects.all()


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def register(self):
        self.save()

    def __str__(self):
        return self.email


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100)

    def __str__(self):
        return self.customer


class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.CharField(max_length=50)
    auth_otp = models.CharField(max_length=5)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user
