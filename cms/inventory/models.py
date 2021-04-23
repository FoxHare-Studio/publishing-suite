import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CatalogTemplate(models.TextChoices):
	BLANK = 'blank', _('Blank')
	CONTENT = 'content', _('Content')
	DEFAULT = 'default', _('Default')
	DESC = 'desc', _('Descriptive')
	SIMPLE = 'simple', _('Simple')
	SIMPLE_ALT = 'simple_alt', _('Simple (Alt.)')
	SIMPLE_DESC = 'simple_desc', _('Simple (Descriptive)')

class categoryType(models.TextChoices):
		COFFEE = 'COFFEE', _('Coffee')
		TEA = 'TEA', _('Tea')

class ProductSet(models.Model):
	## General Info
	name = models.CharField('Name', max_length=190, unique=True)
	description = models.TextField(blank=True, default="")

	## Images
	set_photo = models.ImageField('Product Photo', blank=True, null=True, upload_to='collections/')
	set_catalog_photo = models.ImageField('Catalog Photo', blank=True, null=True, upload_to='collections/')
	
	def __str__(self):
		return self.name
	pass

class Product(models.Model):
	## General Info
	item_name = models.CharField(max_length=190, unique=True)
	item_sku = models.CharField(max_length=190, blank=True, null=True, unique=True)

	category = models.CharField(max_length=32, choices=categoryType.choices, default=categoryType.COFFEE)

	item_description = models.TextField(blank=True, default="")

	class Status(models.TextChoices):
		ACTIVE = 'AC', _('Active')
		CLEARANCE = 'CL', _('Clearance')
		COMINGSOON = 'CS', _('Coming Soon')
		FEATURED = 'FT', _('Featured')
		INACTIVE = 'IN', _('Inactive')
		NEW = 'NW', _('New')

	status = models.CharField(max_length=32, choices=Status.choices, blank=True, default=Status.ACTIVE)

	## Pricing
	cost = models.DecimalField('Cost', max_digits=7, decimal_places=2, blank=True, null=True)
	landed_cost = models.DecimalField('Landed Cost', max_digits=7, decimal_places=2, blank=True, null=True)
	price_wholesale = models.DecimalField(max_digits=7, decimal_places=2, default=0)
	price_retail = models.IntegerField('Retail Price', blank=True, null=True)
	
	## Images
	product_photo = models.ImageField('Product Photo', blank=True, null=True, upload_to='products/')
	product_photo_alt = models.ImageField('Alt. Product Photo', blank=True, null=True, upload_to='products/')
	catalog_photo = models.ImageField('Catalog Photo', blank=True, null=True, upload_to='products/')

	Hidden = models.BooleanField(default=False)

	class grindType(models.TextChoices):
		DRIP = 'DRIP', _('Drip')
		ESPRESSO = 'ESPRESSO', _('Espresso')
		PERC = 'PERC', _('Percolator/Press Pot')
		WHOLEBEAN = 'WHOLEBEAN', _('Whole Bean')

	grind = models.CharField(max_length=32, choices=grindType.choices, blank=True, default=grindType.DRIP)

	product_set = models.BooleanField('Product Set',blank=True, default=False)

	## Publication Status
	catalog = models.BooleanField(blank=True, default=True)
	web = models.BooleanField(blank=True, default=True)
	price_list = models.BooleanField('Price List', blank=True, default=False)

	date_added = models.DateTimeField('Date Added', auto_now_add=True)
	date_modified = models.DateTimeField('Date Modified', auto_now=True)

	def __str__(self):
		return self.item_name
	def recently_added(self):
		return self.date_added >= timezone.now() - datetime.timedelta(days=3)

class Catalog(models.Model):
	section = models.CharField('Section Name', max_length=64, blank=False, unique=True)

	class secTypeOption(models.TextChoices):
		PAGE = 'page', _('Single Page')
		CATEGORY = 'category', _('Category')

	secType = models.CharField('Section Type',max_length=64, choices=secTypeOption.choices, blank=False, default=secTypeOption.PAGE)
	template = models.CharField(max_length=32, choices=CatalogTemplate.choices, blank=True, default=CatalogTemplate.DEFAULT)
	display_photo = models.ImageField('Display Photo', blank=True, null=True, upload_to='catalog/')
	order = models.IntegerField('Catalog Order', blank=False, default=0)
	content = models.TextField(blank=True, null=True)
	class Meta:
		ordering = ["order"]
		verbose_name = "Catalog Section"
		verbose_name_plural = "Catalog"
	def __str__(self):
		return self.section
