from django import forms
from .models import Clinician, ClinicianInvitation, ObjectiveMeasures, PatientClinicianAccess
from django.utils import timezone
from datetime import timedelta
from .joint_choices import (
    ROM_CHOICES, ROM_CHOICES_WITH_FREE, KNEE_FLEXION_CHOICES, KNEE_FLEXION_CHOICES_WITH_FREE,
    KNEE_EXTENSION_CHOICES, HIP_FLEXION_CHOICES, HIP_FLEXION_CHOICES_WITH_FREE,
    HIP_EXTENSION_CHOICES, SHOULDER_FLEXION_CHOICES, SHOULDER_FLEXION_CHOICES_WITH_FREE,
    SHOULDER_ABDUCTION_CHOICES, STRENGTH_CHOICES, JOINT_MEASUREMENTS
)


class ClinicianForm(forms.ModelForm):
    """Form for editing clinician profile"""
    class Meta:
        model = Clinician
        fields = [
            'first_name', 'last_name', 'title', 'registration_body', 'registration_number',
            'speciality', 'organisation', 'email', 'phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name'
            }),
            'title': forms.Select(attrs={
                'class': 'form-select'
            }),
            'registration_body': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select registration body'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Registration number'
            }),
            'speciality': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Speciality'
            }),
            'organisation': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Organisation'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone number'
            }),
        }


class HealthcareFeedbackForm(forms.ModelForm):
    """Form for submitting feedback about healthcare organisations"""
    class Meta:
        from .models import HealthcareFeedback
        model = HealthcareFeedback
        fields = ['organisation', 'rating', 'feedback_type', 'feedback_text', 'is_anonymous', 'is_private']
        widgets = {
            'organisation': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Healthcare organisation name'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'feedback_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Please provide constructive and respectful feedback...'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }


class ClinicianInvitationForm(forms.ModelForm):
    """Form for patients to invite clinicians"""
    class Meta:
        model = ClinicianInvitation
        fields = ['email', 'first_name', 'last_name', 'notes']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'clinician@example.com',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Optional message to the clinician...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        if self.patient:
            # Set default expiration to 30 days
            self.instance.patient = self.patient
            self.instance.expires_at = timezone.now() + timedelta(days=30)


class ObjectiveMeasuresForm(forms.ModelForm):
    """Form for objective measures including joint ROM and power - dynamic based on assessment type"""
    class Meta:
        model = ObjectiveMeasures
        fields = [
            'assessment_date',
            # Store all measurements in JSON fields for flexibility
            'shoulder_rom_left', 'shoulder_rom_right',
            'elbow_rom_left', 'elbow_rom_right',
            'wrist_rom_left', 'wrist_rom_right',
            'hand_rom_left', 'hand_rom_right',
            'hip_rom_left', 'hip_rom_right',
            'knee_rom_left', 'knee_rom_right',
            'ankle_rom_left', 'ankle_rom_right',
            'foot_rom_left', 'foot_rom_right',
            'cervical_rom', 'thoracic_rom', 'lumbar_rom',
            'shoulder_power_left', 'shoulder_power_right',
            'elbow_power_left', 'elbow_power_right',
            'wrist_power_left', 'wrist_power_right',
            'grip_power_left', 'grip_power_right',
            'hip_power_left', 'hip_power_right',
            'knee_power_left', 'knee_power_right',
            'ankle_power_left', 'ankle_power_right',
            'core_power',
            'additional_notes',
        ]
        widgets = {
            'assessment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Additional objective findings...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('assessment', None)
        super().__init__(*args, **kwargs)
        self.assessment = assessment
        
        # Get assessment type to determine which fields to show
        assessment_type = None
        if self.assessment:
            assessment_type = getattr(self.assessment, 'assessment_type', None)
        
        # Always set up dropdowns for physiotherapy assessments or if assessment_type is not set
        # (new assessments will have None, and we assume they're physiotherapy if coming from physiotherapist)
        # Default to True to always show dropdowns unless explicitly not physiotherapy
        should_setup_dropdowns = (assessment_type is None or assessment_type == 'physiotherapy' or assessment_type == '')
        
        # Define joint-specific field configurations
        # Knee fields
        if should_setup_dropdowns:
            # Knee ROM - Flexion
            self.fields['knee_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + KNEE_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'knee', 'data-type': 'rom', 'data-side': 'left', 'data-movement': 'flexion'}
            )
            self.fields['knee_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + KNEE_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'knee', 'data-type': 'rom', 'data-side': 'right', 'data-movement': 'flexion'}
            )
            
            # Knee Strength
            self.fields['knee_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'knee', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['knee_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'knee', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Hip ROM
            self.fields['hip_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + HIP_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hip', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['hip_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + HIP_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hip', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Hip Strength
            self.fields['hip_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hip', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['hip_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hip', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Shoulder ROM
            self.fields['shoulder_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + SHOULDER_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'shoulder', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['shoulder_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + SHOULDER_FLEXION_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'shoulder', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Shoulder Strength
            self.fields['shoulder_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'shoulder', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['shoulder_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'shoulder', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Elbow ROM
            self.fields['elbow_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'elbow', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['elbow_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'elbow', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Elbow Strength
            self.fields['elbow_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'elbow', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['elbow_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'elbow', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Ankle ROM
            self.fields['ankle_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'ankle', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['ankle_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'ankle', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Ankle Strength
            self.fields['ankle_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'ankle', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['ankle_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'ankle', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Spine ROM
            self.fields['cervical_rom'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'spine', 'data-type': 'rom', 'data-region': 'cervical'}
            )
            self.fields['thoracic_rom'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'spine', 'data-type': 'rom', 'data-region': 'thoracic'}
            )
            self.fields['lumbar_rom'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'spine', 'data-type': 'rom', 'data-region': 'lumbar'}
            )
            
            # Core Strength
            self.fields['core_power'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'spine', 'data-type': 'strength', 'data-region': 'core'}
            )
            
            # Wrist ROM
            self.fields['wrist_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'wrist', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['wrist_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                attrs={'class': 'form-select joint-field', 'data-joint': 'wrist', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Wrist Strength
            self.fields['wrist_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'wrist', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['wrist_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'wrist', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Hand ROM
            self.fields['hand_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hand', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['hand_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hand', 'data-type': 'rom', 'data-side': 'right'}
            )
            
            # Grip Strength
            self.fields['grip_power_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hand', 'data-type': 'strength', 'data-side': 'left'}
            )
            self.fields['grip_power_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'hand', 'data-type': 'strength', 'data-side': 'right'}
            )
            
            # Foot ROM
            self.fields['foot_rom_left'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'foot', 'data-type': 'rom', 'data-side': 'left'}
            )
            self.fields['foot_rom_right'].widget = forms.Select(
                choices=[('', 'Normal (default)')] + ROM_CHOICES,
                attrs={'class': 'form-select joint-field', 'data-joint': 'foot', 'data-type': 'rom', 'data-side': 'right'}
            )
        
        # Make all fields optional and ensure they have proper widgets
        for field_name in self.fields:
            if field_name != 'assessment_date' and field_name != 'additional_notes':
                self.fields[field_name].required = False
                # If field doesn't have a Select widget yet and it's a ROM/Power field, set default dropdown
                if not isinstance(self.fields[field_name].widget, forms.Select):
                    if 'rom' in field_name.lower() or 'power' in field_name.lower():
                        # Set up a basic dropdown with ROM or Strength choices
                        if 'rom' in field_name.lower():
                            self.fields[field_name].widget = forms.Select(
                                choices=[('', 'Normal (default)')] + ROM_CHOICES_WITH_FREE,
                                attrs={'class': 'form-select joint-field'}
                            )
                        elif 'power' in field_name.lower():
                            self.fields[field_name].widget = forms.Select(
                                choices=[('', 'Normal (default)')] + STRENGTH_CHOICES,
                                attrs={'class': 'form-select joint-field'}
                            )
                if not hasattr(self.fields[field_name].widget, 'attrs'):
                    self.fields[field_name].widget.attrs = {}
                if 'class' not in self.fields[field_name].widget.attrs:
                    if isinstance(self.fields[field_name].widget, forms.Select):
                        self.fields[field_name].widget.attrs['class'] = 'form-select'
                    else:
                        self.fields[field_name].widget.attrs['class'] = 'form-input'


class ConsentForm(forms.Form):
    """Form for patient consent when connecting with a practitioner via code"""
    consent_medications = forms.BooleanField(
        required=False,
        initial=True,
        label='Medications',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_conditions = forms.BooleanField(
        required=False,
        initial=True,
        label='Conditions',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_allergies = forms.BooleanField(
        required=False,
        initial=True,
        label='Allergies',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_symptoms = forms.BooleanField(
        required=False,
        initial=True,
        label='Symptoms & Assessments',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_personal_info = forms.BooleanField(
        required=False,
        initial=True,
        label='Personal Information',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_emergency_contacts = forms.BooleanField(
        required=False,
        initial=True,
        label='Emergency Contacts',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_work_history = forms.BooleanField(
        required=False,
        initial=True,
        label='Work History',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )
    consent_feedback = forms.BooleanField(
        required=False,
        initial=True,
        label='Healthcare Feedback',
        widget=forms.CheckboxInput(attrs={'class': 'consent-checkbox'})
    )

