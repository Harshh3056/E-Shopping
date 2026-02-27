from django.shortcuts import render,redirect,get_object_or_404
from .models import Add_to_cart, Product, User3056
from django.http import HttpResponse,HttpResponseNotFound
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Coupon
from django.utils import timezone
from django.shortcuts import render
from .models import Add_to_cart, User3056, Wishlist, Categories, Sub_category, Product, Coupon
from django.contrib import messages
from django.conf import settings
from collections import defaultdict
from django.db.models import Sum
from django.core.paginator import Paginator
import razorpay
import random
from .models import*


def login(request):
    if 'email'in request.session:
        return render(request,"index.html")
    try:
        if request.POST:
            email=request.POST['email']
            password=request.POST['password']
            
            uid=User3056.objects.get(email=email)
            if uid.email==email:
                request.session['email']=uid.email
                if uid.password==password:
                    return redirect("index")
                else:   
                    return render(request,"login.html")
            else:
                return render(request,"login.html")
        else:
            return render(request,"login.html")
    except:
        return render(request,"login.html")
    
def profile(request):
    if 'email' not in request.session:
        return redirect('login')  

    try:
        user = User3056.objects.get(email=request.session['email'])
    except User3056.DoesNotExist:
        return redirect('login')  

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        img = request.FILES.get('profile_image')

        if name:
            user.name = name
        if email:
            user.email = email
            request.session['email'] = email 
        if img:
            user.img = img

        user.save()
        return redirect('profile')

    count_wishlist = Wishlist.objects.filter(user_id=user).count()
    count = Add_to_cart.objects.filter(user_id=user).count()
    category = Categories.objects.all().order_by("id")
    sub_category = Sub_category.objects.all().order_by("-id")

    context = {
        "category": category,
        "sub_category": sub_category,
        "count": count,
        "count_wishlist": count_wishlist,
        "user": user
    }

    return render(request, 'profile.html', context)

def register(request):
    if request.POST:
        name=request.POST["name"]
        email=request.POST["email"]
        password=request.POST["password"]
        confirm_password=request.POST["confirm_password"]

        if password == confirm_password:
            User3056.objects.create(name=name,email=email,password=password)
            return redirect("index")
        else:
            con={"emsg":"Password Do not match"}
            return render(request,"register.html",con)
    else:
        return render(request,"register.html")
    
def forget(request):
    if request.POST:
        email=request.POST['email']
        otp=random.randint(1000,9999)
        try:
            user=User3056.objects.get(email=email)
        
            user.otp=otp
            user.save()
            send_mail("django",f"your otp is - {otp}",'harsh30563056@gmail.com',[email])
            contaxt={
                "email":email
            }
            return render(request,"confirm_password.html",contaxt)
        except:
            print("Invalid Email")       
            return render(request,"forgot_password.html") 
    else:
        return render(request,"forgot_password.html")

def confirm_password(request):
    if request.POST:
        email = request.POST['email']
        otp = request.POST['otp']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']

        user = User3056.objects.filter(email=email).first()

        if not user:
            return render(request, "confirm_password.html",
                          {"error_message": "Invalid Email", "email": email})

        if user.otp != int(otp):
            return render(request, "confirm_password.html",
                          {"error_message": "Invalid OTP", "email": email})

        if new_password != confirm_new_password:
            return render(request, "confirm_password.html",
                          {"error_message": "Passwords do not match", "email": email})

        user.password = new_password
        user.save()

        return redirect('login')
    else:
        email = request.GET.get('email')
        return render(request, "confirm_password.html", {"email": email})

def index(request):
    email = request.session.get('email')

    if not email:
        return redirect('login')  
    try:
        user = User3056.objects.get(email=email)
    except User3056.DoesNotExist:
        return HttpResponse("User not found")
    
    context = {}

    if 'email' in request.session:
        try:
            uid = User3056.objects.get(email=request.session['email'])
            context["email"] = request.session['email']
            context["count"] = Add_to_cart.objects.filter(user_id=uid).count()
            context["count_wishlist"] = Wishlist.objects.filter(user_id=uid).count()
        except User3056.DoesNotExist:
            context["email"] = None
            context["count"] = 0
            context["count_wishlist"] = 0
    else:
        context["email"] = None
        context["count"] = 0
        context["count_wishlist"] = 0

    context["category"] = Categories.objects.all().order_by("id")
    context["sub_category"] = Sub_category.objects.all().order_by("-id")

    return render(request, "index.html", context)

def logout(request):
    request.session.delete()
    return redirect("login") 

def wishlist(request):
    category = Categories.objects.all().order_by("id")
    sub_category = Sub_category.objects.all().order_by("-id")
    con={"category":category,"sub_category":sub_category}
    return render(request,"wishlist.html",con)

def cart(request):
    email = request.session.get('email')

    if not email:
        return redirect('login') 

    try:
        user = User3056.objects.get(email=email)
    except User3056.DoesNotExist:
        return HttpResponse("User not found")
    
    if 'email' in request.session:
        uid = User3056.objects.get(email=request.session['email'])
        category = Categories.objects.all().order_by("id")
        sub_category = Sub_category.objects.all().order_by("-id")
        prod = Add_to_cart.objects.filter(user_id=uid)
        cid = Add_to_cart.objects.filter(user_id=uid)
        count = prod.count()
        count_wishlist = Wishlist.objects.filter(user_id=uid).count()
        pid = Product.objects.all().order_by("-id")

        sub_total = 0
        charge = 50
        discount = 0
        discount_percent = 0
        applied_coupon = None
        coupon_error = ""

        for i in prod:
            sub_total += i.quantity * i.price

        if request.method == "POST":
            code = request.POST.get("coupon_code", "").strip()
            try:
                coupon = Coupon.objects.get(code=code)
                if coupon.is_valid():
                    discount_percent = coupon.discount_percent
                    discount = (sub_total * discount_percent) // 100
                    applied_coupon = coupon
                    request.session['discount'] = discount
                    request.session['coupon_code'] = coupon.code
                    request.session['discount_percent'] = discount_percent
                else:
                    coupon_error = "Coupon is expired or inactive."
                    request.session['discount'] = 0
                    request.session['coupon_code'] = ""
                    request.session['discount_percent'] = 0
            except Coupon.DoesNotExist:
                coupon_error = "Invalid coupon code."
                request.session['discount'] = 0
                request.session['coupon_code'] = ""
                request.session['discount_percent'] = 0
        else:
            discount = request.session.get("discount", 0)
            discount_percent = request.session.get("discount_percent", 0)
            coupon_code = request.session.get("coupon_code", "")
            if coupon_code:
                try:
                    applied_coupon = Coupon.objects.get(code=coupon_code)
                except Coupon.DoesNotExist:
                    applied_coupon = None

        grand_total = sub_total + charge - discount

        context = {
            "user_id": uid,
            "product_id": pid,
            "cid": cid,
            "total": grand_total,
            "sub_total": sub_total,
            "charge": charge,
            "discount": discount,
            "discount_percent": discount_percent,
            "applied_coupon": applied_coupon,
            "coupon_error": coupon_error,
            "count": count,
            "count_wishlist": count_wishlist,
            "category": category,
            "sub_category": sub_category,
            "grand_total": grand_total
        }

        return render(request, "cart.html", context)

    else:
        return render(request, "cart.html")


def checkout(request):
    email = request.session.get('email')

    if not email:
        return redirect('login') 
    try:
        user = User3056.objects.get(email=request.session['email'])
    except User3056.DoesNotExist:
        return HttpResponse("User not found")

    uid = user
    count_wishlist = Wishlist.objects.filter(user_id=uid).count()
    count = Add_to_cart.objects.filter(user_id=uid).count()
    category = Categories.objects.all().order_by("id")
    sub_category = Sub_category.objects.all().order_by("-id")

    cart_items_product = Add_to_cart.objects.filter(user_id=uid)

    subtotal = 0
    for item in cart_items_product:
        if item.price and item.quantity:
            item.total_price = item.price * item.quantity
            item.save()
            subtotal += item.total_price

    discount = request.session.get("discount", 0)
    coupon_code = request.session.get("coupon_code", "")
    shipping = 50
    final_total = subtotal + shipping - discount
    client = razorpay.Client(auth=('rzp_test_uqhoYnBzHjbvGF', 'jEhBs6Qp9hMeGfq5FyU45cVi'))
    response = client.order.create({
                'amount': int(final_total * 100),
                'currency': 'INR',
                'payment_capture': 1
            })

    print("Razorpay response:", response)
    context = {
        "category": category,
        "sub_category": sub_category,
        "count": count,
        "count_wishlist": count_wishlist,
        "cart_items_product": cart_items_product,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "final_total": final_total,
        "coupon_code": coupon_code,
        "response": response
    }

    return render(request, "checkout.html", context)



def contact(request):
    if "email" in request.session:
        uid=User3056.objects.get(email=request.session['email'])
        count_wishlist=Wishlist.objects.filter(user_id=uid).count()
        count=Add_to_cart.objects.filter(user_id=uid).count()
        category = Categories.objects.all().order_by("id")
        sub_category = Sub_category.objects.all().order_by("-id")


        if request.POST:
            name=request.POST['name']
            email=request.POST['email']
            subject=request.POST['subject']
            msg=request.POST['msg']
            Contact.objects.create(name=name,email=email,subject=subject,msg=msg)

        con={"category":category,"sub_category":sub_category,"count":count,"count_wishlist":count_wishlist}
        return render(request,"contact.html",con)
    else:
        return render(request,"login.html")


def detail(request):
    uid=User3056.objects.get(email=request.session['email'])
    count_wishlist=Wishlist.objects.filter(user_id=uid).count()
    count=Add_to_cart.objects.filter(user_id=uid).count()
    category = Categories.objects.all().order_by("id")
    sub_category = Sub_category.objects.all().order_by("-id")
    con={"category":category,"sub_category":sub_category,"count":count,"count_wishlist":count_wishlist}
    return render(request,"detail.html",con)

def detail1(request,id):
    uid=User3056.objects.get(email=request.session['email'])
    count_wishlist=Wishlist.objects.filter(user_id=uid).count()
    count=Add_to_cart.objects.filter(user_id=uid).count()
    pid = Product.objects.get(id=id)
    con={"pid":pid,"count":count,"count_wishlist":count_wishlist}
    return render(request,'detail.html',con)

def add_to_cart(request,id):
    if 'email' in request.session:
        uid=User3056.objects.get(email=request.session['email'])
        pid=Product.objects.get(id=id)
        cart_items = Add_to_cart.objects.filter(product_id=pid,user_id=uid).first()
        if cart_items:
            cart_items.quantity += 1
            cart_items.total_price = cart_items.quantity * cart_items.price
            cart_items.save()
        else:
            Add_to_cart.objects.create(
            user_id=uid,
                product_id=pid,
                name=pid.name,
                price=pid.price,
                image=pid.image,
                quantity=1,
                total_price=pid.price
            )
        return redirect("cart")
    else:
        return render(request,"login.html")

def shop(request, subcategory_name=None):
    email = request.session.get('email')

    if not email:
        return redirect('login') 

    try:
        user = User3056.objects.get(email=email)
    except User3056.DoesNotExist:
        return HttpResponse("User not found")
    
    user = User3056.objects.get(email=request.session['email'])
    uid = user

    wishlist_items = Wishlist.objects.filter(user_id=user)
    wishlist_ids = [item.product_id.id for item in wishlist_items]

    category = Categories.objects.all().order_by("-id")
    sub_category = Sub_category.objects.all().order_by("-id")
    prices = Price.objects.all()
    size1 = Size.objects.all()
    color1 = Colour.objects.all()

    count_wishlist = Wishlist.objects.filter(user_id=uid).count()
    count = Add_to_cart.objects.filter(user_id=uid).count()

    pid = Product.objects.all()

    if subcategory_name:
        try:
            subcat = Sub_category.objects.get(name=subcategory_name)
            pid = Product.objects.filter(sub_category=subcat)
        except Sub_category.DoesNotExist:
            pid = Product.objects.none()

    else:
        piz2 = request.GET.get('piz2')  # price
        piz3 = request.GET.get('piz3')  # size
        piz4 = request.GET.get('piz4')  # color
        sort = request.GET.get('sort')
        order = request.GET.get('order', 'asc')
        search_query = request.GET.get('q')

        if piz2:
            pid = Product.objects.filter(price1=piz2)
        elif piz3:
            pid = Product.objects.filter(size1=piz3)
        elif piz4:
            pid = Product.objects.filter(color1=piz4)
        elif sort == "lth":
            pid = Product.objects.order_by("price")
        elif sort == "htl":
            pid = Product.objects.order_by("-price")
        elif sort == "atz":
            pid = Product.objects.order_by("name")
        elif sort == "zta":
            pid = Product.objects.order_by("-name")

        if search_query:
            pid = pid.filter(name__icontains=search_query)
        
    paginator=Paginator(pid,6)  
    page_number=request.GET.get("page",1)  
    pid=paginator.get_page(page_number)
    show_page=paginator.get_elided_page_range(page_number,on_each_side=2,on_ends=1)

    context = {
        "pid": pid,
        "category": category,
        "sub_category": sub_category,
        "count_wishlist": count_wishlist,
        "count": count,
        "prices": prices,
        "size1": size1,
        "color1": color1,
        "sort": request.GET.get('sort'),
        "current_order": request.GET.get('order', 'asc'),
        "search_query": request.GET.get('q'),
        'wishlist_ids': wishlist_ids,
        'show_page':show_page
    }

    return render(request, 'shop.html', context)

def incr(request,id):
    inc=Add_to_cart.objects.get(id=id)
    if inc:
        inc.quantity += 1
        inc.total_price = inc.quantity * inc.price
        inc.save()
    return redirect("cart")

def decr(request,id):
    inc=Add_to_cart.objects.get(id=id)
    if inc:
        inc.quantity -= 1
        inc.total_price = inc.quantity * inc.price
        inc.save()
    if inc.quantity == 0:
        inc.total_price = inc.quantity * inc.price
        inc.delete()
    return redirect("cart")

def rem(request,id):
    inc=Add_to_cart.objects.get(id=id)
    inc.delete()
    return redirect("cart")

def add_to_wishlist(request, id):
    uid = User3056.objects.get(email=request.session['email'])
    pid = Product.objects.get(id=id)
    wish_id = Wishlist.objects.filter(product_id=pid, user_id=uid).first()
    
    if wish_id:
        wish_id.delete()
        messages.info(request, "Removed")
    else:
        Wishlist.objects.create(
            user_id=uid,
            product_id=pid,
            price=pid.price,
            name=pid.name,
            image=pid.image,
        )
        messages.info(request, "Added")

    return redirect('shop')
    
def rem_wishlist(request, id):
    d=Wishlist.objects.get(id=id)
    d.delete()
    return redirect('wishlist')

def wishlist(request):
    uid=User3056.objects.get(email=request.session['email'])
    category = Categories.objects.all().order_by("-id")
    sub_category = Sub_category.objects.all().order_by("-id")
    add_product=Wishlist.objects.filter(user_id=uid) 
    count_wishlist=Wishlist.objects.filter(user_id=uid).count()
    count=Add_to_cart.objects.filter(user_id=uid).count()
    
    con={"uid":uid,"add_product":add_product,"count":count,"count_wishlist":count_wishlist, "category":category,
        "sub_category":sub_category}
    
    return render(request,"wishlist.html",con)

def order(request):
    email = request.session.get('email')

    if not email:
        return redirect('login')  
    try:
        user = User3056.objects.get(email=request.session['email'])
    except User3056.DoesNotExist:
        return HttpResponse("User not found")

    count_wishlist = Wishlist.objects.filter(user_id=user).count()
    count = Add_to_cart.objects.filter(user_id=user).count()
    category = Categories.objects.all().order_by("id")
    sub_category = Sub_category.objects.all().order_by("-id")

    if request.method == "POST":
        BillingAddress.objects.create(
            user_id=user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            mobile_no=request.POST.get("mobile_no"),
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            country=request.POST.get("country"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            zip_code=request.POST.get("zip_code")
        )

        cart_items = Add_to_cart.objects.filter(user_id=user)
        if cart_items.exists():
            shipping = 50
            subtotal = sum(item.total_price for item in cart_items)

            discount_percent = request.session.get("discount_percent", 0)
            discount = (subtotal * discount_percent) // 100 
            grand_total = subtotal + shipping - discount

            new_order = Order.objects.create(
                user_id=user,
                discount=discount,
                total_price=grand_total
            )

            for item in cart_items:
                Orderitem.objects.create(
                    order=new_order,
                    user_id=user,
                    product_id=item.product_id,
                    name=item.name,
                    price_order=item.price,
                    image=item.image,
                    quantity_order=item.quantity,
                    total_price_order=item.total_price
                )

            cart_items.delete()
            request.session.pop("discount", None)
            request.session.pop("discount_percent", None)
            request.session.pop("coupon_code", None)

        return redirect('order')

    orders = Order.objects.filter(user_id=user).order_by("created_at")
    order_data = []

    for order in orders:
        items = order.items.all()
        if not items.exists():
            continue

        subtotal = sum(item.total_price_order for item in items)
        shipping = 50
        discount = order.discount or 0
        discount_percent = round((discount / subtotal) * 100) if subtotal > 0 else 0
        grand_total = subtotal + shipping - discount

        order_data.append({
            "order": order,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "discount": discount,
            "discount_percent": discount_percent,
            "grand_total": grand_total
        })

    context = {
        "category": category,
        "sub_category": sub_category,
        "count": count,
        "count_wishlist": count_wishlist,
        "orders": order_data
    }

    return render(request, "order.html", context)

def cancel_order(request,id):
    d=Order.objects.get(id=id)
    d.delete()
    return redirect('order')

def detail1(request, id):
    email = request.session.get('email')
    if not email:
        return redirect('login') 
    try:
        user = User3056.objects.get(email=email)
    except User3056.DoesNotExist:
        return HttpResponse("User not found")
    
    uid=User3056.objects.get(email=request.session['email'])
    category = Categories.objects.all().order_by("-id")
    sub_category = Sub_category.objects.all().order_by("-id")
    count_wishlist=Wishlist.objects.filter(user_id=uid).count()
    count=Add_to_cart.objects.filter(user_id=uid).count()
    pid = Product.objects.get(id=id)
    pid = get_object_or_404(Product, id=id)
    reviews = Review.objects.filter(product=pid).order_by('-created_at')

    total_reviews = reviews.count()
    total_stars = sum([review.rating for review in reviews])

    avg_rating = round(total_stars / total_reviews, 1) if total_reviews > 0 else 0

    full_stars = int(avg_rating)
    half_star = 1 if avg_rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    if request.method == 'POST':
        Review.objects.create(
            product=pid,
            name=request.POST['name'],
            email=request.POST['email'],
            rating=request.POST['rating'],
            review=request.POST['review']
        )
        return redirect('detail1', id=id)

    return render(request, 'detail.html', {
        'pid': pid,
        'category':category,
        'sub_category':sub_category,
        'count_wishlist':count_wishlist,
        'count':count,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'full_stars': full_stars,
        'half_star': half_star,
        'empty_stars': empty_stars
    })


