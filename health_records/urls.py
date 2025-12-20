from django.urls import path
from . import views

app_name = 'health_records'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('passport/', views.passport_view, name='passport'),
    path('passport/<int:patient_id>/', views.passport_view, name='passport_patient'),
    path('emergency-card/', views.emergency_card, name='emergency_card'),
    path('verify-clinician/<int:clinician_id>/', views.verify_clinician, name='verify_clinician'),
    path('verify-clinician/', views.verify_clinician_registration, name='verify_clinician_registration'),
    
    # Medication URLs
    path('medications/add/', views.add_medication, name='add_medication'),
    path('medications/<int:pk>/edit/', views.edit_medication, name='edit_medication'),
    path('medications/<int:pk>/delete/', views.delete_medication, name='delete_medication'),
    
    # Condition URLs
    path('conditions/add/', views.add_condition, name='add_condition'),
    path('conditions/<int:pk>/edit/', views.edit_condition, name='edit_condition'),
    path('conditions/<int:pk>/delete/', views.delete_condition, name='delete_condition'),
    
    # Allergy URLs
    path('allergies/add/', views.add_allergy, name='add_allergy'),
    path('allergies/<int:pk>/edit/', views.edit_allergy, name='edit_allergy'),
    path('allergies/<int:pk>/delete/', views.delete_allergy, name='delete_allergy'),
    
    # Assessment/Symptoms URLs (User-entered)
    path('assessments/add/', views.add_assessment, name='add_assessment'),
    path('assessments/<int:pk>/edit/', views.edit_assessment, name='edit_assessment'),
    path('assessments/<int:pk>/delete/', views.delete_assessment, name='delete_assessment'),
    
    # Practitioner Assessment URLs
    path('assessments/<int:assessment_pk>/practitioner/add/', views.add_practitioner_assessment, name='add_practitioner_assessment'),
    path('assessments/<int:pk>/practitioner/edit/', views.edit_practitioner_assessment, name='edit_practitioner_assessment'),
    
    # Profile URL
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Work History URLs
    path('work-history/add/', views.add_work_history, name='add_work_history'),
    path('work-history/<int:pk>/edit/', views.edit_work_history, name='edit_work_history'),
    path('work-history/<int:pk>/delete/', views.delete_work_history, name='delete_work_history'),
    
    # Healthcare Feedback URLs
    path('feedback/add/', views.add_feedback, name='add_feedback'),
    path('feedback/add/<int:access_pk>/', views.add_feedback, name='add_feedback_for_access'),
    path('feedback/view/', views.view_feedback, name='view_feedback'),
    path('feedback/<int:pk>/delete/', views.delete_feedback, name='delete_feedback'),
    
    # Clinician Invitation URLs
    path('clinicians/invite/', views.invite_clinician, name='invite_clinician'),
    path('clinicians/revoke/<int:access_pk>/', views.revoke_clinician_access, name='revoke_clinician_access'),
    
    # Azure Document Intelligence URLs
    path('assessments/<int:assessment_pk>/process-notes/', views.process_notes_image, name='process_notes_image'),
    path('assessments/<int:assessment_pk>/findings/', views.view_extracted_findings, name='view_extracted_findings'),
    path('assessments/<int:assessment_pk>/findings/json/', views.get_extracted_findings_json, name='get_extracted_findings_json'),
    path('findings/<int:finding_pk>/verify/', views.verify_finding, name='verify_finding'),
    path('findings/<int:finding_pk>/delete/', views.delete_finding, name='delete_finding'),
]

