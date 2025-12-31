from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # List and Add Products
    path('', views.products, name='products'),

    # Edit a Product
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),

    # Delete a Product (POST only)
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # List and Add Vendors
    path('vendors/', views.vendor_details, name='vendor_details'),

    # Edit and Delete Vendors
    path('vendors/edit/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),

    # Delete a Vendor (POST only)
    path('vendors/delete/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),

    # Stock Receiving Details
    path('stock-receiving/', views.stock_receiving_list, name='stock_receiving_list'),
    
    
    path('sales/', views.sales, name='sales'),

    path('Sales_return/', views.sale_return, name='Sale_return'),
    
    path('get-sale-details/', views.get_sale_details, name='get_sale_details'),


    path('ajax/get-product/', views.get_product_by_barcode, name='get_product_by_barcode'),
    
   ]
