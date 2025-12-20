from django.urls import path
from . import views

app_name = 'clinicians'

urlpatterns = [
    path('login/', views.practitioner_login, name='practitioner_login'),
    path('signup/<uuid:token>/', views.clinician_signup, name='signup'),
    path('dashboard/', views.practitioner_dashboard, name='dashboard'),
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/<int:patient_id>/', views.client_detail, name='client_detail'),
    path('quick-upload/select-client/', views.select_client_for_quick_upload, name='select_client_quick_upload'),
    path('api/clients-list/', views.clients_list_json, name='clients_list_json'),
    path('profile/edit/', views.edit_clinician_profile, name='edit_profile'),
    path('profile/delete/', views.delete_clinician_profile, name='delete_profile'),
    path('patient/<int:patient_id>/assessment/create/', views.create_assessment, name='create_assessment'),
    path('patient/<int:patient_id>/assessment/quick-upload/', views.quick_upload_assessment, name='quick_upload_assessment'),
    path('objective-measures/<int:assessment_pk>/add/', views.add_objective_measures, name='add_objective_measures'),
    path('objective-measures/<int:pk>/edit/', views.edit_objective_measures, name='edit_objective_measures'),
    path('send-practitioner-code/', views.send_practitioner_code_email, name='send_practitioner_code_email'),
]

