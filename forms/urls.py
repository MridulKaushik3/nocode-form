from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('form/<int:form_id>/', views.fill_form, name='fill_form'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/form/create/', views.create_form, name='create_form'),
    path('dashboard/form/<int:form_id>/responses/', views.form_responses, name='form_responses'),
    path('dashboard/form/<int:form_id>/fields/', views.add_fields, name='add_fields'),
    path(
    'dashboard/form/<int:form_id>/export/',
    views.export_responses_csv,
    name='export_responses_csv'
),
    path('dashboard/form/<int:form_id>/duplicate/', views.duplicate_form, name='duplicate_form'),
    path('dashboard/form/<int:form_id>/delete/', views.delete_form, name='delete_form'),

]
