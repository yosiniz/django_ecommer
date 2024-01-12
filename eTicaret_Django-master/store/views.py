from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render,get_object_or_404
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from .models import Customer 

# views.py

from django.shortcuts import render
from .models import Category

def your_view_function(request):
    categories = Category.objects.all()
    print(categories)  # Konsolda kategorilerin görünmesini kontrol etmek için
    context = {'categories': categories}
    return render(request, 'store/store.html', context)

def store(request):
	data = cartData(request)
	categories = Category.objects.all()
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products,'categories': categories, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def register_request(request):
	if request.method=="POST":
		username=request.POST.get('username')		
		email=request.POST.get('email')		
		firstname=request.POST.get('firstname') 			
		lastname=request.POST.get('lastname')
		password=request.POST.get('password')
		repassword=request.POST.get('repassword')

		if password==repassword:
			if User.objects.filter(username=username).exists():
				return render (request,'store/register_request.html',{"error":"username kullanılıyor"})
			else:
				if User.objects.filter(email=email).exists():
					return render (request,'store/register_request.html',{"error":"mail kullanılıyorr"})
				else:
					user=User.objects.create_user(username=username,email=email,first_name=firstname,last_name=lastname,password=password)
					user.save()
					Customer.objects.create(user=user, name=f"{firstname} {lastname}", email=email)
					return redirect("auth_login")
		else:
			return render (request,'store/register_request.html',{"error":"parolalar eşleşmiyor"})
	return render(request, 'store/register_request.html' )
		

def auth_login (request):
	if request.method=='POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		# myuser=User.objects.filter(email=email)
		myuser=authenticate(username=username,password=password)
		if myuser  is not None:
			login(request,myuser)
			return redirect("/")
		else:
			return render(request,'store/auth_login.html',{
			"error":"email yada şifre bilgileriniz yanlış"
		})

	return render(request, 'store/auth_login.html' )


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)