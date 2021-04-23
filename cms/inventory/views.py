import csv, decimal, logging, io, mathfilters
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from .models import Catalog, Product, ProductSet

## Catalog
def catalog(request):
	catalog_section = Catalog.objects.all().order_by('order')
	category = Category.objects.all()
	collection = Collection.objects\
		.filter(catalog = "1")\
		.exclude(status = "H")\
		.order_by('name')
	bedrooms = collection.filter(category_id=6)
	mattresses = collection.filter(category_id=7)
	living_room_stationary = collection.filter(category_id=12)
	living_room_motion = collection.filter(category_id=8)
	recliners = collection.filter(category_id=11)
	dining = collection.filter(category_id=3)
	occasionals = collection.filter(category_id=9)
	product_set = Product.objects\
		.exclude(group=1)\
		.exclude(product_set=1)\
		.filter(visibility=1)\
		.order_by('collection_order')
	return render(request, 'catalog/catalog.html', {
		'catalog_section': catalog_section,
		'category': category,
		'collection': collection,
		'bedrooms': bedrooms,
		'mattresses': mattresses,
		'living_room_stationary': living_room_stationary,
		'living_room_motion': living_room_motion,
		'recliners': recliners,
		'dining': dining,
		'occasionals': occasionals,
		'product_set': product_set,
	})

## Dashboard
def dashboard(request):
	products = Product.objects.order_by('-date_added')[:5]
	return render(request, 'dashboard/index.html', {
		'products': products,
	})

### Dashboard Detail
def detail(request, collection_id):
	collection = get_object_or_404(Collection, pk=collection_id)
	product_set = Product.objects\
		.exclude(product_set=1)\
		.filter(collection_id=collection_id)\
		.order_by('collection_order')
	return render(request, 'dashboard/detail.html', {
		'collection': collection,
		'product_set': product_set,
	})

### Product Set Index
def product_sets(request):
	object_list = Collection.objects.all()
	return render(request, 'dashboard/search_results.html', {
		'object_list': object_list
	})

### Search Results
class SearchResultsView(ListView):
	model = Product
	template_name = 'dashboard/search_results.html'

	def get_queryset(self):
		query = self.request.GET.get('q')
		object_list = Product.objects.filter(
			Q(item_name__icontains=query) | Q(item_sku__icontains=query) | Q(item_description__icontains=query)
		)
		return object_list

## Pricelist
def pricelist(request, pricelist_type):
	pricelist_section = Pricelist.objects.all().order_by('order')
	category = Category.objects.all()
	collection = Collection.objects\
		.filter(price_list = "1")\
		.exclude(status = "H")\
		.order_by('name')
	product_set = Product.objects\
		.exclude(product_set=1)\
		.filter(visibility=1)\
		.order_by('collection_order')
	pricelist_type = pricelist_type
	return render(request, 'pricelist/index.html', {
		'collection': collection,
		'product_set': product_set,
		'pricelist_type': pricelist_type,
		'pricelist_section': pricelist_section,
	})

## Reports

### AMP Report
def amp(request):
	page_title = "Amp Report"
	products = Product.objects\
		.exclude(collection__status="IN")\
		.exclude(product_set=1)\
		.exclude(view_type="H")\
		.exclude(visibility=False)\
		.filter(collection__amp=True)\
		.order_by('collection')\
		.order_by('collection__vendor__in')
	return render(request, 'dashboard/amp.html', {'page_title': page_title, 'products': products})

### MicroD Report
def microd(request):
	page_title = "MicroD Report"
	products = Product.objects\
		.exclude(collection__status="IN")\
		.exclude(view_type="H")\
		.exclude(visibility=False)\
		.filter(collection__cfc=True)\
		.order_by('collection')\
		.order_by('collection__vendor__in')
	return render(request, 'dashboard/microd.html', {
		'page_title': page_title,
		'products': products,
	})

### NPI Report
def npi(request, collection_id):
	collection = get_object_or_404(Collection, pk=collection_id)
	product_set = Product.objects.filter(collection_id=collection_id).order_by('collection_order')
	return render(request, 'npi/detail.html', {
		'collection': collection,
		'product_set':product_set
	})

## Documentation
def documentation(request):
	return render(request, 'dashboard/documentation.html')

## Exports

### Amp Export
def export_amp(request):
	products = Product.objects.all()\
		.exclude(collection__status="IN")\
		.exclude(view_type="H")\
		.exclude(product_set=1)\
		.exclude(visibility=False)\
		.filter(collection__amp=True)\
		.order_by('collection')\
		.order_by('collection__vendor__in')

	def cartons():
		if p.cartons == 1:
			return "1 CARTON"
		if p.cartons > 1:
			return str(p.cartons)+" CARTONS"
		else:
			return "N/A"

	def product_dimensions():
		if p.p_width:
			return str(floatformat(p.p_width))+'"x'+str(floatformat(p.p_length))+'"x'+str(floatformat(p.p_height))+'"'
		else:
			return ""

	def shipping_dimensions():
		if p.s_width:
			return str(floatformat(p.s_width))+'x'+str(floatformat(p.s_length))+'x'+str(floatformat(p.s_height))
		else:
			return ""

	def product_description():
		if p.item_description:
			return p.item_name+' - '+p.item_description
		else:
			return p.item_name
	
	def retail_price():
		if p.price_retail:
			return p.price_retail
		else:
			return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.retail_margin))

	def ecomm_price():
		if p.price_e:
			return p.price_e
		else:
			return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.ecomm_margin))

	def product_surcharge():
		if p.collection.container_surcharge:
			return 'May be subject to a Container Surcharge'

	def product_new():
		if p.collection.new_arrival:
			return "Yes"

	def product_special():
		if p.collection.special:
			return "Closeout"

	def product_simon_li():
		if p.collection.simon_li:
			return "Express"

	def product_visibility():
		if p.visibility:
			return "Exclusive"

	def product_photoset():
		if p.product_photo5:
			return p.collection.set_photo.url[19:]+', '+p.product_photo1.url[16:]+', '+p.product_photo2.url[16:]+', '+p.product_photo3.url[16:]+', '+p.product_photo4.url[16:]+', '+p.product_photo5.url[16:]
		if p.product_photo4:
			return p.collection.set_photo.url[19:]+', '+p.product_photo1.url[16:]+', '+p.product_photo2.url[16:]+', '+p.product_photo3.url[16:]+', '+p.product_photo4.url[16:]
		if p.product_photo3:
			return p.collection.set_photo.url[19:]+', '+p.product_photo1.url[16:]+', '+p.product_photo2.url[16:]+', '+p.product_photo3.url[16:]
		if p.product_photo2:
			return p.collection.set_photo.url[19:]+', '+p.product_photo1.url[16:]+', '+p.product_photo2.url[16:]
		if p.product_photo1:
			return p.collection.set_photo.url[19:]+', '+p.product_photo1.url[16:]
		if p.collection.set_photo:
			return p.collection.set_photo.url[19:]

	fieldnames = [
		'Order',
		'Item',
		'(WxLxH)',
		'Weight (lbs)',
		'Cubes',
		'Carton(s)',
		'Shipping(WxLxH)',
		'Page Title',
		'Description',
		'Price',
		'Price I',
		'Price E',
		'Suggested Retail',
		'Lifestyle Price',
		'Surcharge',
		'Romance',
		'Category',
		'Preferred Vendor',
		'Photo Name',
		'New Arrivals',
		'Specials',
		'Simon Li',
		'Item Visibility',
		'Page ID',
		'Photo Set'
	]

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Amp_Report.csv"'
	writer = csv.DictWriter(response, fieldnames=fieldnames, restval='')
	writer.writeheader()

	for p in products:
		writer.writerow({
			'Order': p.collection.category.amp_id,
			'Item': str(p.collection)+' '+str(p.item_name),
			'(WxLxH)': product_dimensions(),
			'Weight (lbs)': p.p_weight,
			'Cubes': p.cubes,
			'Carton(s)': cartons(),
			'Shipping(WxLxH)': shipping_dimensions(),
			'Page Title': p.collection,
			'Description': product_description(),
			'Price': p.price_rnd,
			'Price I': p.price_i,
			'Price E': p.price_e,
			'Suggested Retail': retail_price(),
			'Lifestyle Price': p.price_lifestyle,
			'Surcharge': product_surcharge(),
			'Romance': p.collection.romance,
			'Category': p.collection.category,
			'Preferred Vendor': p.collection.vendor,
			'Photo Name': product_photoset(),
			'New Arrivals': product_new(),
			'Specials': product_special(),
			'Simon Li': product_simon_li(),
			'Item Visibility': product_visibility(),
			'Page ID': p.collection,
			'Photo Set': product_photoset()
		})

	return response

### MicroD Export
def export_mircod_report(request):
	collections = Collection.objects.exclude(vendor__in=[27,29,8,25,10,11,12,18,31,21,22])
	products = Product.objects.all()\
		.exclude(collection__vendor__in=[27,29,8,25,10,11,12,18,31,21,22])\
		.exclude(collection__status="IN")\
		.exclude(view_type="H")\
		.exclude(visibility=False)\
		.filter(collection__cfc=True)\
		.order_by('collection')\
		.order_by('collection__vendor__in')
		
	products_active = products.all()
	category_data = Category.objects.all()

	def bed_size():
		if p.bed_size:
			return p.get_bed_size_display()

	def department():
		if p.collection.category.name == "Mattresses":
			return "Mattresses"
		elif p.collection.category.name == "Foundations":
			return "Mattresses"
		else:
			return "Furniture"

	def display_price():
		return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.cfc_margin), 0)

	# Truncate path names from photos ('/media/products/', '/media/collections/')
	def photo_url1():
		if p.product_photo1:
			return p.product_photo1.url[16:]
		elif p.collection.set_photo:
			return p.collection.set_photo.url[19:]

	def photo_url2():
		if p.product_photo2:
			return p.product_photo2.url[16:]

	def photo_url3():
		if p.product_photo3:
			return p.product_photo3.url[16:]

	def photo_url4():
		if p.product_photo4:
			return p.product_photo4.url[16:]

	def photo_url5():
		if p.product_photo5:
			return p.product_photo5.url[16:]

	def sku_status():
		if p.collection.status == 'AC':
			return "Active"
		elif p.collection.status == 'PO':
			return "Clearance"
		elif p.collection.status == 'FT':
			return "Featured Product"

	def variation():
		if p.bed_size:
			return "Bed Size"

	fieldnames = [
		'CATALOG CODE',
		'BRAND',
		'MANUFACTURER SKU',
		'SHOW',
		'NEW SKU',
		'PRICE TYPE',
		'DISPLAY PRICE',
		'ITEM RANK',
		'SELL ONLINE',
		'IS TAXABLE',
		'VIEW TYPE',
		'SKU STATUS',
		'CONDITION',
		'SHORT DESCRIPTION',
		'TYPE',
		'SUBTYPE',
		'COLOR',
		'PHOTO1',
		'PHOTO2',
		'PHOTO3',
		'PHOTO4',
		'PHOTO5',
		'DEPARTMENT',
		'ROOM',
		'COLLECTION',
		'PRODUCT DESCRIPTION',
		'HEIGHT',
		'WIDTH',
		'LENGTH',
		'WEIGHT',
		'VOLUME',
		'BED SIZE',
		'IS PRODUCT GROUP',
		'VARIATION'
	]

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="MicroD_Report.csv"'
	writer = csv.DictWriter(response, fieldnames=fieldnames, restval='N/A')
	writer.writeheader()

	for p in products:
		writer.writerow({
			'CATALOG CODE': "P20529",
			'BRAND': p.collection.vendor,
			'MANUFACTURER SKU': p.item_sku,
			'SHOW': "Y",
			'NEW SKU': p.item_sku,
			'PRICE TYPE': "OverRide",
			'DISPLAY PRICE': display_price(),
			'ITEM RANK': "9998",
			'SELL ONLINE': "Y",
			'IS TAXABLE': "Y",
			'VIEW TYPE': p.get_view_type_display(),
			'SKU STATUS': sku_status(),
			'CONDITION': "New",
			'SHORT DESCRIPTION': p.item_name,
			'TYPE': p.item_type,
			'SUBTYPE': p.item_subtype,
			'COLOR': p.collection.colors,
			'PHOTO1': photo_url1(),
			'PHOTO2': photo_url2(),
			'PHOTO3': photo_url3(),
			'PHOTO4': photo_url4(),
			'PHOTO5': photo_url5(),
			'DEPARTMENT': department(),
			'ROOM': p.collection.category.microd_name,
			'COLLECTION': p.collection,
			'PRODUCT DESCRIPTION': p.collection.romance,
			'HEIGHT': floatformat(p.p_height),
			'WIDTH': floatformat(p.p_width),
			'LENGTH': floatformat(p.p_length),
			'WEIGHT': floatformat(p.p_weight),
			'VOLUME': floatformat(p.cubes),
			'BED SIZE': p.get_bed_size_display(),
			'IS PRODUCT GROUP': p.product_set,
			'VARIATION': variation(),
		})

	return response
	
### Collection Export
def export_collections(request):
	collection = Collection.objects\
		.order_by('name')\
		.order_by('vendor')

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="collections.csv"'

	writer = csv.writer(response)
	writer.writerow([
		'Name',
		'Category',
		'Status',
		'Vendor',
		'Color(s)',
		'Color Code',
		'AMP',
		'Catalog',
		'CFC',
		'Price List',
		'Notes'
	])

	for c in collection:
		writer.writerow([
			c.name,
			c.category,
			c.get_status_display(),
			c.vendor,
			c.colors,
			str(c.color_code),
			c.amp,
			c.catalog,
			c.cfc,
			c.price_list,
			c.tracker_notes
		])

	return response

### Product Export
def export_products(request):
	products = Product.objects.all()\
		.order_by('collection')\
		.order_by('collection__vendor__in')\
		.exclude(product_set=1)\

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Product_Export.csv"'

	def item():
		if p.item_description:
			return p.item_name+' '+p.item_description
		else:
			return p.item_name

	def image_check():
		if p.product_photo1:
			return "Y"

	def price_retail():
		if p.price_retail:
			return floatformat(p.price_retail, 0)
		else:
			return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.retail_margin), 0)

	def price_ecomm():
		if p.price_i:
			return floatformat(p.price_e, 0)
		else:
			return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.ecomm_margin), 0)

	def price_cfc():
		return floatformat(decimal.Decimal(p.price_rnd)*decimal.Decimal(p.collection.vendor.cfc_margin), 0)

	writer = csv.writer(response)
	writer.writerow([
		'Collection',
		'SKU',
		'Item',
		'Vendor',
		'Price (WS)',
		'Price (Retail)',
		'Price (E-Comm)',
		'Price (CFC.com)',
		'Item Type',
		'View Type',
		'Visibility',
		'Status',
		'Carton(s)',
		'AMP',
		'CFC',
		'Photo(s)',
		'Notes'
	])

	for p in products:
		writer.writerow([
			p.collection,
			p.item_sku,
			item(),
			p.collection.vendor,
			p.price_rnd,
			price_retail(),
			price_ecomm(),
			price_cfc(),
			p.item_type,
			p.get_view_type_display(),
			p.visibility,
			p.collection.get_status_display(),
			p.cartons,
			p.collection.amp,
			p.collection.cfc,
			image_check(),
			p.collection.tracker_notes
		])

	return response
