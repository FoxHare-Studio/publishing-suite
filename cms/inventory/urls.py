from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import SearchResultsView

from . import views

app_name = 'inventory'
urlpatterns = [
	path('', views.dashboard, name='dashboard'),
	path('admin/', admin.site.urls),
	path('catalog/', views.catalog, name='catalog'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('search/', SearchResultsView.as_view(), name='search_results'),
	path('detail/<int:product_id>/', views.detail, name='detail'),
	path('pricelist/<int:pricelist_type>', views.pricelist, name='pricelist'),
	path('help/', views.documentation, name='documentation'),
	#path('test/', views.test, name='test'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
