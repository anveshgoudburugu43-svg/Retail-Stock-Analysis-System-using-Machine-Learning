from django.urls import path
from django.contrib import admin
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Landing page
    path('', views.about, name='about'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),

    path('logout/', views.custom_logout, name='logout'),


    # Home (Dashboard)
    path('home/', views.home, name='home'),
    path('restock/', views.restock_recommendations, name='restock_recommendations'),

    # Stock Management
    path('add/', views.add_stock, name='add_stock'),
    path('edit/<int:pk>/', views.edit_stock, name='edit_stock'),
    path('delete/<int:pk>/', views.delete_stock, name='delete_stock'),

    # Sales Management
    path('sale/', views.sale_view, name='sale'),
    # Sales Management
    path('sale/<int:stock_id>/', views.add_sale, name='add_sale'),
    path('sales/', views.sales_overview, name='sales_overview'),
    path('export-sales/', views.export_sales, name='export_sales'),

  


    

    # Admin Panel
    path('admin/', admin.site.urls),
]
