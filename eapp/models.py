from django.db import models
from django.utils import timezone
from django.contrib import admin

class User3056(models.Model):
    name=models.CharField(max_length=20,blank=True,null=True)
    email=models.EmailField(unique=True,blank=True,null=True)
    password=models.CharField(max_length=25,blank=True,null=True)
    otp=models.IntegerField(blank=True,null=True)
    profile_image = models.ImageField(upload_to='img/', default='img/default.png')

    def __str__(self):
        return self.name
# Create your models here.

class Categories(models.Model):
    name=models.CharField(max_length=20,blank=True,null=True)

    def __str__(self):
        return self.name
    
class Sub_category(models.Model):
    cid=models.ForeignKey(Categories,on_delete=models.CASCADE,blank=True,null=True)
    name=models.CharField(max_length=20,blank=True,null=True)

    def __str__(self):
        return self.name
    
class Price(models.Model):
    name=models.CharField(max_length=90,blank=True,null=True)

    def __str__(self):
        return self.name
    
class Size(models.Model):
    name=models.CharField(max_length=90,blank=True,null=True)

    def __str__(self):
        return self.name
    
class Colour(models.Model):
    name=models.CharField(max_length=90,blank=True,null=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    main_category=models.ForeignKey(Categories,on_delete=models.CASCADE,blank=True,null=True)
    sub_category=models.ForeignKey(Sub_category,on_delete=models.CASCADE,blank=True,null=True)
    price1=models.ForeignKey(Price,on_delete=models.CASCADE,blank=True,null=True)
    size1=models.ForeignKey(Size,on_delete=models.CASCADE,blank=True,null=True)
    color1=models.ForeignKey(Colour,on_delete=models.CASCADE,blank=True,null=True)
    name=models.CharField(max_length=90,blank=True,null=True)
    price=models.IntegerField()
    del_price=models.IntegerField()
    image=models.ImageField(upload_to="media",blank=True,null=True)
    des=models.TextField()

    def __str__(self):
        return self.name

class Add_to_cart(models.Model):
    user_id=models.ForeignKey(User3056,on_delete=models.CASCADE,blank=True,null=True)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
    name=models.CharField(max_length=90,blank=True,null=True)
    price=models.IntegerField()
    image=models.ImageField(upload_to="media",blank=True,null=True)
    quantity=models.IntegerField(blank=True,null=True)
    total_price=models.IntegerField()

    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user_id=models.ForeignKey(User3056,on_delete=models.CASCADE,blank=True,null=True)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
    name=models.CharField(max_length=90,blank=True,null=True)
    price=models.IntegerField()
    image=models.ImageField(upload_to="media",blank=True,null=True)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)  
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to
    
class BillingAddress(models.Model):
    user_id = models.ForeignKey(User3056, on_delete=models.CASCADE, blank=True, null=True, related_name='billing_addresses')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    user_id = models.ForeignKey(User3056, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)     
    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"Order #{self.id}"


class Orderitem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    user_id = models.ForeignKey(User3056, on_delete=models.CASCADE, blank=True, null=True, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='ordered_products')
    name = models.CharField(max_length=90, blank=True, null=True)
    price_order = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to="media", blank=True, null=True)
    quantity_order = models.IntegerField(blank=True, null=True)
    total_price_order = models.IntegerField()

    def __str__(self):
        return f"{self.name} x {self.quantity_order}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.PositiveIntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.product.name}"
    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'email', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'email', 'review')


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    msg = models.CharField(max_length=100)
