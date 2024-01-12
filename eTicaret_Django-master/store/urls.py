from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from . import views
# class CustomLogoutView(LogoutView):
#     next_page = reverse_lazy('auth_login')

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('auth_login', views.auth_login, name="auth_login"),
	path('register_request', views.register_request, name="register_request"),
	path('checkout/', views.checkout, name="checkout"),
    # Diğer URL pattern'ları buraya ekleyebilirsiniz
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    path('products/', views.your_view_function, name='your_app_name_product_list'),
    path('logout/', LogoutView.as_view(), name='logout')

]