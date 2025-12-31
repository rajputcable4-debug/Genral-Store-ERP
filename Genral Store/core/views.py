from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.db import IntegrityError, transaction
from django.utils import timezone
from .models import *
from django.db.models import Max
import json
from datetime import datetime





# -----------------------------
# List Products and Add Product
# -----------------------------
def products(request):
    """
    Display all products and handle adding a new product via POST.
    """

    # Get all products
    products = StockAssigned.objects.all().order_by('item_code')
    form_errors = False

    # Generate next auto item_code (6 digits)
    last_item = StockAssigned.objects.order_by('-id').first()
    if last_item and last_item.item_code.isdigit():
        next_item_code = str(int(last_item.item_code) + 1).zfill(6)
    else:
        next_item_code = "000001"

    if request.method == 'POST':
        # Always use auto-generated item_code
        item_code = next_item_code
        product_name = request.POST.get('product_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        specification = request.POST.get('specification', '').strip()

        # Validate required fields
        if not product_name or not company_name:
            form_errors = True
            messages.error(request, "Please fill in all required fields.")

        else:
            try:
                with transaction.atomic():
                    StockAssigned.objects.create(
                        item_code=item_code,
                        product_name=product_name,
                        company_name=company_name,
                        specification=specification or ''
                    )
                messages.success(request, f"Product '{product_name}' added successfully.")
                return redirect('products')

            except IntegrityError:
                form_errors = True
                messages.error(request, "Could not add product due to a database error.")

    
    return render(request, 'products.html', locals())



# -----------------------------
# Edit Product
# -----------------------------

def edit_product(request, product_id):
    """
    Edit an existing product.
    """
    product = get_object_or_404(StockAssigned, id=product_id)
    form_data = {
        'item_code': product.item_code,
        'product_name': product.product_name,
        'company_name': product.company_name,
        'specification': product.specification or ''
    }

    if request.method == 'POST':
        item_code = request.POST.get('item_code', '').strip()
        product_name = request.POST.get('product_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        specification = request.POST.get('specification', '').strip()

        # Preserve submitted values for re-rendering on error
        form_data.update({
            'item_code': item_code,
            'product_name': product_name,
            'company_name': company_name,
            'specification': specification
        })

        # Validate required fields
        if not item_code or not product_name or not company_name:
            messages.error(request, "Please fill in all required fields.")
        elif StockAssigned.objects.filter(item_code__iexact=item_code).exclude(pk=product.pk).exists():
            messages.error(request, f"Item code '{item_code}' already exists.")
        else:
            try:
                with transaction.atomic():
                    product.item_code = item_code
                    product.product_name = product_name
                    product.company_name = company_name
                    product.specification = specification
                    product.save()
                messages.success(request, f"Product '{product_name}' updated successfully.")
                return redirect('products')
            except IntegrityError:
                messages.error(request, "Could not update product due to a database error. Please try again.")

    return render(request, 'edit_product.html', {'product': product, 'form_data': form_data})


# -----------------------------
# Delete Product
# -----------------------------

def delete_product(request, product_id):
    """
    Delete a product only via POST to prevent accidental deletion via GET.
    """
    product = get_object_or_404(StockAssigned, id=product_id)
    if request.method != 'POST':
        return redirect('products')
    product_name = product.product_name
    product.delete()
    messages.success(request, f"Product '{product_name}' deleted successfully.")
    return redirect('products')


# ----------------------------------------------------
# SHOW VENDORS + ADD NEW VENDOR
# ----------------------------------------------------
def vendor_details(request):
    vendors = VenderDetails.objects.all().order_by('vender_code')
    form_errors = False

    # Auto-generate next vendor code (6 digits)
    last_vendor = VenderDetails.objects.order_by('-id').first()
    if last_vendor and last_vendor.vender_code.isdigit():
        next_vendor_code = str(int(last_vendor.vender_code) + 1).zfill(6)
    else:
        next_vendor_code = "000001"

    # Handle POST - Add Vendor
    if request.method == 'POST':
        vender_code = request.POST.get('vender_code', '').strip()
        vender_name = request.POST.get('vender_name', '').strip()
        vender_number = request.POST.get('vender_number', '').strip()
        company_name = request.POST.get('company_name', '').strip()

        # Validation
        if not vender_code or not vender_name or not company_name:
            form_errors = True
            messages.error(request, "Vendor Code, Vendor Name, and Company Name are required.")
        elif VenderDetails.objects.filter(vender_code__iexact=vender_code).exists():
            form_errors = True
            messages.error(request, f"Vendor with code '{vender_code}' already exists.")
        else:
            try:
                with transaction.atomic():
                    VenderDetails.objects.create(
                        vender_code=vender_code,
                        vender_name=vender_name,
                        vender_number=vender_number,
                        company_name=company_name
                    )
                messages.success(request, f"Vendor '{vender_name}' added successfully.")
                return redirect('vendor_details')
            except IntegrityError:
                form_errors = True
                messages.error(request, "Database error! Could not add vendor. Try again.")

    context = {
        'vendors': vendors,
        'next_vendor_code': next_vendor_code,
        'form_errors': form_errors
    }

    return render(request, 'vendor.html', context)


# ----------------------------------------------------
# EDIT VENDOR
# ----------------------------------------------------
def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(VenderDetails, id=vendor_id)

    if request.method == 'POST':
        vendor.vender_name = request.POST.get('vender_name', '').strip()
        vendor.vender_number = request.POST.get('vender_number', '').strip()
        vendor.company_name = request.POST.get('company_name', '').strip()

        if not vendor.vender_name or not vendor.company_name:
            messages.error(request, "Vendor name and company name cannot be empty.")
            # Re-render the edit form so the user can correct input
            return render(request, 'edit_vendor.html', {'vendor': vendor})

        vendor.save()
        messages.success(request, "Vendor updated successfully.")
        return redirect('vendor_details')

    return render(request, 'edit_vendor.html', {'vendor': vendor})


# ----------------------------------------------------
# DELETE VENDOR
# ----------------------------------------------------
def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(VenderDetails, id=vendor_id)

    if request.method == 'POST':
        vendor.delete()
        messages.success(request, "Vendor deleted successfully.")
        return redirect('vendor_details')

    return redirect('vendor_details')







# ----------------------------------------------------
def generate_order_number():
    last_order = StockReceivingDetail.objects.aggregate(
        max_no=Max('order_number')
    )['max_no']

    if last_order and last_order.isdigit():
        return str(int(last_order) + 1).zfill(7)
    return "0000001"


def stock_receiving_list(request):
    receive_number = generate_order_number()

    print('receive_number', receive_number)
    today_date = timezone.now().date()

    vendors = VenderDetails.objects.all()
    products = StockAssigned.objects.all()

    if request.method == "POST":
        vendor_raw = request.POST.get('vendor')
        if not vendor_raw:
            messages.error(request, "Please select a vendor.")
            return redirect('stock_receiving_list')

        try:
            vendor_code = vendor_raw.split('-')[0]
            vendor = VenderDetails.objects.get(vender_code=vendor_code)
        except VenderDetails.DoesNotExist:
            messages.error(request, "Selected vendor does not exist.")
            return redirect('stock_receiving_list')

        rows_json = request.POST.get('rows', '[]')
        try:
            rows = json.loads(rows_json)
        except json.JSONDecodeError:
            messages.error(request, "Invalid product data format.")
            return redirect('stock_receiving_list')

        if not rows:
            messages.error(request, "No products added.")
            return redirect('stock_receiving_list')

        errors = []

        # -----------------------------
        # CALCULATE TOTALS FIRST
        # -----------------------------
        total_qty = 0
        total_amount = Decimal('0.00')

        for row in rows:
            qty = int(row.get('qty', 0))
            rate = Decimal(row.get('rate', '0'))
            total_qty += qty
            total_amount += qty * rate

        try:
            with transaction.atomic():

                # -----------------------------
                # CREATE HEADER (ONCE)
                # -----------------------------
                stockreceving.objects.create(
                    order_number=receive_number,
                    order_date=today_date,
                    vender_code=vendor.vender_code,
                    vendor_name=vendor.vender_name,
                    total_qty=total_qty,
                    total_amount=total_amount
                )

                # -----------------------------
                # CREATE DETAILS
                # -----------------------------
                for idx, row in enumerate(rows, start=1):
                    product = StockAssigned.objects.get(
                        item_code=row.get('item_code')
                    )

                    barcode = row.get('barcode_number')
                    qty = int(row.get('qty', 0))
                    rate = Decimal(row.get('rate', '0'))
                    sale_rate = Decimal(row.get('sale_rate', '0'))

                    exp_date = row.get('exp_date')
                    print('exp_date', exp_date)
                    exp_date = (
                        datetime.strptime(exp_date, "%Y-%m-%d").date()
                        if exp_date else None
                    )

                    if StockReceivingDetail.objects.filter(
                        barcode_number=barcode
                    ).exists():
                        raise ValueError(
                            f"Row {idx}: Barcode '{barcode}' already exists."
                        )

                    StockReceivingDetail.objects.create(
                        order_number=receive_number,
                        order_date=today_date,
                        vender=vendor,
                        product=product,
                        barcode_number=barcode,
                        qty=qty,
                        rate=rate,
                        sale_rate=sale_rate,
                        expire_date=exp_date
                    )

                    ItemStock.objects.create(
                        order_number=receive_number,
                        vender_code=vendor.vender_code,
                        item_code=product.item_code,
                        product_name=product.product_name,
                        company_name=product.company_name,
                        specification=product.specification,
                        barcode_number=barcode,
                        total_qty=qty,
                        rate=rate,
                        sale_rate=sale_rate,
                        expire_date=exp_date,
                        sale_qty=0,
                        sale_return_qty=0,
                        stock_return_qty=0,
                        
                    )


        except Exception as e:
            messages.error(request, str(e))
            return redirect('stock_receiving_list')

        messages.success(request, "Stock received successfully.")
        return redirect('stock_receiving_list')

    return render(request, "stock_receiving.html", locals())

from django.http import JsonResponse
from .models import ItemStock

def get_product_by_barcode(request):
    barcode = request.GET.get('barcode')
    print('barcode:', barcode)

    if not barcode:
        return JsonResponse({}, status=200)

    stock_detail = ItemStock.objects.filter(
        barcode_number=barcode
    ).first()

    print('stock_detail:', stock_detail)

    # Silent fail if not found
    if not stock_detail:
        return JsonResponse({})

    # Out of stock check
    if stock_detail.available_qty <= 0:
        return JsonResponse({
            'item_code': stock_detail.item_code,
            'qty': 0
        })

    data = {
    'item_code': stock_detail.item_code,
    'product_name': stock_detail.product_name,
    'company_name': stock_detail.company_name,
    'specification': stock_detail.specification or '',
    'sale_rate': stock_detail.sale_rate,   # ✅ numeric
    'qty': 1,                               # ✅ each scan adds 1
    'available_qty': stock_detail.available_qty
    }


    return JsonResponse(data)







def generate_sale_number():
    last_sale = SaleInfo.objects.aggregate(
        max_no=Max('sale_number')
    )['max_no']

    if last_sale and last_sale.isdigit():
        return str(int(last_sale) + 1).zfill(7)

    return "0000001"




from datetime import date


def sales(request):
    if request.method == "POST":
        try:
            with transaction.atomic():

                # 🔐 Generate sale number ONLY here
                sale_number = generate_sale_number()

                sale_date = request.POST.get("sale_date")
                customer_name = request.POST.get("customer_name")
                customer_contact = request.POST.get("contact_number", "")
                total_quantity = int(request.POST.get("total_quantity", 0) or 0)
                total_amount = Decimal(request.POST.get("total_amount", "0.00") or 0)
                cash_received = Decimal(request.POST.get("cash_received", "0.00") or 0)
                cash_return = Decimal(request.POST.get("cash_return", "0.00") or 0)

                sale_info = SaleInfo.objects.create(
                    sale_number=sale_number,
                    sale_date=sale_date,
                    customer_name=customer_name,
                    customer_contact=customer_contact,
                    total_quantity=total_quantity,
                    total_amount=total_amount,
                    cash_received=cash_received,
                    cash_return=cash_return
                )

                # --- Sale Detail ---
                barcodes = request.POST.getlist("barcode[]")
                item_codes = request.POST.getlist("item_code[]")
                product_names = request.POST.getlist("product_name[]")
                company_names = request.POST.getlist("company_name[]")
                specifications = request.POST.getlist("specification[]")
                quantities = request.POST.getlist("qty[]")
                sale_rates = request.POST.getlist("sale_rate[]")
                amounts = request.POST.getlist("amount[]")

                for i in range(len(barcodes)):
                    if not barcodes[i].strip():
                        continue

                    qty = int(quantities[i] or 0)

                    # ✅ Backend stock validation
                    stock = ItemStock.objects.select_for_update().get(
                        barcode_number=barcodes[i],
                        item_code=item_codes[i]
                    )

                    if stock.available_qty < qty:
                        raise Exception(
                            f"Insufficient stock for {stock.product_name}"
                        )

                    SaleDetail.objects.create(
                        sale=sale_info,  # <-- must link to the sale
                        barcode_number=barcodes[i],
                        item_code=item_codes[i],
                        product_name=product_names[i],
                        company_name=company_names[i],
                        specification=specifications[i] or '',
                        qty=qty,
                        sale_rate=Decimal(sale_rates[i] or 0),
                        amount=Decimal(amounts[i] or 0)
                    )

                    # ✅ ONLY update sale_qty
                    stock.sale_qty += qty
                    stock.save()

                messages.success(request, "Sale recorded successfully!")
                return redirect('sales')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('sales')

    # GET request
    context = {
        "today": date.today().strftime("%Y-%m-%d"),
        "sale_number": generate_sale_number()
    }
    return render(request, "sale.html", context)






from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import SaleInfo, SaleDetail

def get_sale_details(request):
    sale_number = request.GET.get('sale_number')
    if not sale_number:
        return JsonResponse({'error': 'Sale number not provided'}, status=400)

    try:
        sale = SaleInfo.objects.get(sale_number=sale_number)
        sale_items = SaleDetail.objects.filter(sale=sale)  # ✅ directly use the ForeignKey

        data = {
            'sale_date': sale.sale_date.strftime('%Y-%m-%d'),
            'customer_name': sale.customer_name,
            'customer_contact': sale.customer_contact,
            'items': [
                {
                    'barcode': item.barcode_number,
                    'item_code': item.item_code,
                    'description': item.product_name,
                    'specification': item.specification or '',
                    'qty': item.qty,
                    'sale_rate': float(item.sale_rate),
                    'amount': float(item.amount)
                }
                for item in sale_items
            ]
        }
        return JsonResponse(data)
    except SaleInfo.DoesNotExist:
        return JsonResponse({'error': 'Sale not found'}, status=404)






def generate_return_number():
    last_return = SaleReturnDetail.objects.order_by('-id').first()

    if last_return and last_return.return_number.isdigit():
        next_number = int(last_return.return_number) + 1
    else:
        next_number = 1

    return str(next_number).zfill(6)






def sale_return(request):
    today = timezone.now().date()
    return_number = generate_return_number()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # -----------------------
                # MAIN RETURN INFO
                # -----------------------
                sale_number = request.POST.get('sale_number', '')
                sale_date = request.POST.get('sale_date') or None
                customer_name = request.POST.get('customer_name', '')
                customer_contact = request.POST.get('contact_number', '')
                return_number = request.POST.get('return_number') or generate_return_number()
                return_date = request.POST.get('return_date') or None
                reason = request.POST.get('return_reason', '')

                # -----------------------
                # TABLE DATA
                # -----------------------
                barcodes = request.POST.getlist('barcode[]')
                descriptions = request.POST.getlist('description[]')
                specifications = request.POST.getlist('specification[]')
                qtys = request.POST.getlist('qty[]')
                sale_amounts = [Decimal(r or '0.00') for r in request.POST.getlist('sale_rate[]')]
                amounts = [Decimal(a or '0.00') for a in request.POST.getlist('amount[]')]

                # -----------------------
                # CALCULATE ORIGINAL SALE TOTAL (STATIC)
                # -----------------------
                original_total_amount = sum(sale_amounts[i] * int(qtys[i] or 0) for i in range(len(qtys)))

                # -----------------------
                # CALCULATE REFUND AMOUNT
                # -----------------------
                total_quantity = sum(int(q or 0) for q in qtys)
                amount_refunded = sum(int(qtys[i] or 0) * sale_amounts[i] for i in range(len(qtys)))

                # -----------------------
                # SAVE HEADER
                # -----------------------
                return_detail = SaleReturnDetail.objects.create(
                    sale_number=sale_number,
                    sale_date=sale_date,
                    customer_name=customer_name,
                    customer_contact=customer_contact,
                    return_number=return_number,
                    return_date=return_date,
                    reason_for_return=reason,
                    total_quantity=total_quantity,
                    total_amount=original_total_amount,  # STATIC
                    amount_refunded=amount_refunded      # DYNAMIC
                )

                # -----------------------
                # SAVE EACH ITEM AND UPDATE STOCK
                # -----------------------
                rows = min(len(barcodes), len(qtys), len(sale_amounts), len(amounts))

                for i in range(rows):
                    barcode = barcodes[i].strip()
                    if not barcode:
                        continue

                    qty = int(qtys[i] or 0)
                    if qty <= 0:
                        continue

                    # Save SaleReturn item
                    SaleReturn.objects.create(
                        return_detail=return_detail,
                        barcode_number=barcode,
                        description=descriptions[i],
                        specification=specifications[i],
                        qty=qty,
                        sale_amount=sale_amounts[i],
                        total_amount=sale_amounts[i] * qty  # Use returned qty
                    )

                    # Update ItemStock
                    try:
                        stock_item = ItemStock.objects.get(barcode_number=barcode)
                        stock_item.sale_return_qty += qty
                        stock_item.save()  # available_qty auto-updates
                    except ItemStock.DoesNotExist:
                        pass

                # -----------------------
                # REDIRECT AFTER ALL ROWS PROCESSED
                # -----------------------
                return redirect('Sale_return')

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'sale_return.html', {
        'today': today,
        'return_number': return_number
    })









