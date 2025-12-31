from django.contrib import admin
from django.apps import apps

from .models import *

@admin.register(StockAssigned)
class StockAssignedAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'product_name', 'company_name', 'specification')
    search_fields = ('item_code', 'product_name', 'company_name')
    ordering = ('item_code',)

@admin.register(VenderDetails)
class VenderDetailsAdmin(admin.ModelAdmin):
    list_display = ('vender_code', 'vender_name', 'vender_number', 'company_name')
    search_fields = ('vender_code', 'vender_name', 'company_name')
    ordering = ('vender_code',)

@admin.register(StockReceivingDetail)
class StockReceivingDetailAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date', 'vender', 'product', 'barcode_number', 'qty', 'rate', 'sale_rate', 'expire_date')
    search_fields = ('order_number', 'barcode_number', 'vender__vender_name', 'product__product_name')
    ordering = ('order_number',)

@admin.register(CustomerSaleInvoice)
class CustomerSaleInvoiceAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'sale_date', 'customer_name', 'total_quantity', 'total_amount', 'cash_received', 'cash_return')
    search_fields = ('sale_number', 'customer_name')
    ordering = ('sale_number',)

@admin.register(stockreceving)
class StockReceivingAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date', 'vender_code', 'vendor_name', 'total_qty', 'total_amount')
    search_fields = ('order_number', 'vender_code', 'vendor_name')
    ordering = ('order_number',)

@admin.register(ItemStock)
class ItemStockAdmin(admin.ModelAdmin): 
    list_display = (
        'order_number', 'vender_code', 'item_code', 'product_name', 'company_name', 
        'specification', 'barcode_number', 'total_qty', 'sale_qty', 
        'sale_return_qty',  'available_qty', 'rate', 'sale_rate', 'expire_date'
    )
    search_fields = ('order_number', 'vender_code', 'item_code', 'product_name', 'company_name', 'barcode_number')
    ordering = ('order_number',)

@admin.register(SaleInfo)
class SaleInfoAdmin(admin.ModelAdmin):
    list_display = (
        'sale_number', 'sale_date', 'customer_name', 'customer_contact', 
        'total_quantity', 'total_amount', 'cash_received', 'cash_return',
    )
    search_fields = ('sale_number', 'customer_name', 'customer_contact')
    ordering = ('sale_number',)

@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        'barcode_number', 'item_code', 'product_name', 'company_name', 
        'specification', 'qty', 'sale_rate', 'amount'
    )
    search_fields = ('barcode_number', 'item_code', 'product_name')
    ordering = ('barcode_number',)





@admin.register(SaleReturnDetail)
class SaleReturnDetailAdmin(admin.ModelAdmin):
    list_display = (
        'return_number',
        'sale_number',
        'return_date',
        'customer_name',
        'total_quantity',
        'total_amount',
        'amount_refunded',
        'reason_for_return'
    )

    search_fields = (
        'return_number',
        'sale_number',
        'customer_name',
        'customer_contact',
    )

    list_filter = (
        'return_date',
    )

    ordering = ('-return_date',)

    readonly_fields = ('return_number',)

    fieldsets = (
        ('Sale Information', {
            'fields': (
                'sale_number',
                'sale_date',
            )
        }),
        ('Customer Information', {
            'fields': (
                'customer_name',
                'customer_contact',
            )
        }),
        ('Return Information', {
            'fields': (
                'return_number',
                'return_date',
                'reason_for_return',
            )
        }),
        ('Totals', {
            'fields': (
                'total_quantity',
                'total_amount',
                'amount_refunded',
            )
        }),
    )


@admin.register(SaleReturn)
class SaleReturnAdmin(admin.ModelAdmin):
    list_display = (
        'barcode_number',
        'description',
        'qty',
        'sale_amount',
        'total_amount',
    )

    search_fields = (
        'barcode_number',
        'description',
    )

    list_filter = (
        'sale_amount',
    )

    ordering = ('barcode_number',)

    fieldsets = (
        ('Product Information', {
            'fields': (
                'barcode_number',
                'description',
                'specification',
            )
        }),
        ('Return Quantity & Pricing', {
            'fields': (
                'qty',
                'sale_amount',
                'total_amount',
            )
        }),
    )



# Auto-register any remaining models not explicitly registered
app = apps.get_app_config('core')
for model_name, model in app.models.items():
    if model in admin.site._registry:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        continue
