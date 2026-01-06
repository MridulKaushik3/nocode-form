from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Public views
    path('', views.home, name='home'),
    path('form/<int:form_id>/', views.fill_form, name='fill_form'),

    # Dashboard / Admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/form/create/', views.create_form, name='create_form'),
    path('dashboard/form/<int:form_id>/edit/', views.edit_form, name='edit_form'),
    path('dashboard/form/<int:form_id>/fields/', views.add_fields, name='add_fields'),
    path('dashboard/form/<int:form_id>/responses/', views.form_responses, name='form_responses'),
    path('dashboard/form/<int:form_id>/export/', views.export_responses_csv, name='export_responses_csv'),
    path('dashboard/form/<int:form_id>/duplicate/', views.duplicate_form, name='duplicate_form'),
    path('dashboard/form/<int:form_id>/delete/', views.delete_form, name='delete_form'),
    path('field/<int:field_id>/delete/', views.delete_field, name='delete_field'),
    path('field/<int:field_id>/edit/', views.edit_field, name='edit_field'),


]
