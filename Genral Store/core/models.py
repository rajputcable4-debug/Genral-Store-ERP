from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class StockAssigned(models.Model):
    item_code = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    specification = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.item_code} - {self.product_name}"

    class Meta:
        ordering = ['item_code']


class VenderDetails(models.Model):
    # Consider renaming to "VendorDetails" in a future migration for correct spelling.
    vender_code = models.CharField(max_length=50, unique=True)
    vender_name = models.CharField(max_length=100)
    vender_number = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.vender_code} - {self.vender_name}"



class stockreceving(models.Model):
    order_number= models.CharField(max_length=50)
    order_date= models.DateField()
    vender_code= models.CharField(max_length=50)
    vendor_name= models.CharField(max_length=100)
    total_qty= models.PositiveIntegerField(validators=[MinValueValidator(0)])
    total_amount= models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])



class StockReceivingDetail(models.Model):
    order_number = models.CharField(max_length=50)
    order_date = models.DateField()
    vender = models.ForeignKey(VenderDetails, on_delete=models.PROTECT, related_name='receivings')
    product = models.ForeignKey(StockAssigned, on_delete=models.PROTECT, related_name='receivings')
    barcode_number = models.CharField(max_length=50, unique=True)
    qty = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    rate = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    sale_rate = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    expire_date = models.DateField(blank=True, null=True)

    
    def __str__(self):
        return f"{self.order_number} - {self.product.product_name}"

    class Meta:
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['barcode_number']),
        ]


from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class ItemStock(models.Model):
    order_number = models.CharField(max_length=50)
    vender_code = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50, default='')
    product_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    specification = models.CharField(max_length=255, blank=True, null=True)
    barcode_number = models.CharField(max_length=50)
    total_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    sale_rate = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    rate = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    expire_date = models.DateField(blank=True, null=True)
    sale_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    sale_return_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    stock_return_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    available_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)

    def save(self, *args, **kwargs):
        self.available_qty = (
            self.total_qty
            - self.sale_qty
            + self.sale_return_qty
            - self.stock_return_qty
        )
        super().save(*args, **kwargs)







class CustomerSaleInvoice(models.Model):
    sale_number = models.CharField(max_length=50, unique=True)
    sale_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=20, blank=True, null=True)
    total_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    cash_received = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    cash_return = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    def __str__(self):
        return self.sale_number

    class Meta:
        ordering = ['-sale_date']




class SaleReturnDetail(models.Model):
    sale_number = models.CharField(max_length=50, default='')
    sale_date = models.DateField(null=True, blank=True)

    customer_name = models.CharField(max_length=100, default='')
    customer_contact = models.CharField(max_length=20, blank=True, null=True)

    return_number = models.CharField(max_length=50, unique=True)
    return_date = models.DateField(null=True, blank=True)

    total_quantity = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    amount_refunded = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    reason_for_return = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.return_number



class SaleReturn(models.Model):
    return_detail = models.ForeignKey(
        SaleReturnDetail,
        on_delete=models.CASCADE,
        related_name='items',
        
    )

    barcode_number = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    specification = models.CharField(max_length=255, blank=True, null=True)

    qty = models.PositiveIntegerField(default=1)
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))



class ExchangeSale(models.Model):
    exchange_number = models.CharField(max_length=50, unique=True)
    sale_invoice = models.ForeignKey(CustomerSaleInvoice, on_delete=models.CASCADE, related_name='exchange_sales')
    return_invoice = models.ForeignKey(SaleReturn, on_delete=models.CASCADE, null=True, blank=True, related_name='exchange_sales')
    exchange_date = models.DateField()
    total_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    refund_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    cash_received = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    cash_return = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    def __str__(self):
        return self.exchange_number


class ExchangeSaleDetail(models.Model):
    exchange_sale = models.ForeignKey(ExchangeSale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(StockAssigned, on_delete=models.PROTECT, related_name='exchange_sale_details')
    barcode_number = models.CharField(max_length=50)
    qty = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])



class SaleInfo(models.Model):
    sale_number = models.CharField(max_length=50, unique=True)
    sale_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=20, blank=True, null=True)
    total_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]
    )
    cash_received = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]
    )
    cash_return = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self):
        return self.sale_number


class SaleDetail(models.Model):
    sale = models.ForeignKey(SaleInfo, on_delete=models.CASCADE, related_name='details')
    barcode_number = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    specification = models.CharField(max_length=255, blank=True, null=True)
    qty = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=1)
    sale_rate = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self):
        return f"{self.product_name} ({self.item_code})"

    
