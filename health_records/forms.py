from django import forms
from .models import Medication, Condition, Allergy, Assessment
from accounts.models import UserProfile


class MedicationForm(forms.ModelForm):
    """Form for adding/editing medications"""
    class Meta:
        model = Medication
        fields = [
            'name', 'dosage', 'frequency', 'start_date', 'end_date',
            'is_prescribed', 'prescribing_clinician', 'prescription_image', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Paracetamol'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 500mg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Twice daily'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'prescribing_clinician': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Clinician name (if prescribed)'
            }),
            'prescription_image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'capture': 'environment'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
            'is_prescribed': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }


class ConditionForm(forms.ModelForm):
    """Form for adding/editing conditions"""
    class Meta:
        model = Condition
        fields = ['name', 'diagnosis_date', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Type 2 Diabetes'
            }),
            'diagnosis_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }


class AllergyForm(forms.ModelForm):
    """Form for adding/editing allergies"""
    class Meta:
        model = Allergy
        fields = ['allergen', 'reaction', 'severity', 'date_identified', 'notes']
        widgets = {
            'allergen': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Penicillin, Peanuts'
            }),
            'reaction': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Describe the allergic reaction...'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_identified': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Additional notes...'
            }),
        }


class AssessmentForm(forms.ModelForm):
    """Form for users to add their symptoms"""
    class Meta:
        model = Assessment
        fields = ['current_symptoms', 'previous_symptoms', 'condition_progression', 'pain_level', 'symptom_date']
        widgets = {
            'current_symptoms': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Describe your current symptoms...'
            }),
            'previous_symptoms': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Describe any previous symptoms that have resolved or changed...'
            }),
            'condition_progression': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'How has your condition progressed over time?'
            }),
            'pain_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'type': 'number',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'symptom_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }


class PractitionerAssessmentForm(forms.ModelForm):
    """Form for practitioners to add assessment data - different fields based on practitioner type"""
    class Meta:
        model = Assessment
        fields = [
            'assessment_type', 'assessment_date', 'completed_at',
            # Subjective fields (for physiotherapists)
            'current_symptoms', 'previous_symptoms', 'condition_progression', 'pain_level', 'symptom_date',
            # Objective fields
            'objective_findings', 'treatment_plan', 'practitioner_notes', 'practitioner_notes_image'
        ]
        widgets = {
            'assessment_type': forms.Select(
                choices=[
                    ('', 'Select assessment type...'),
                    ('physiotherapy', 'Physiotherapy'),
                    ('general', 'General Health Check'),
                    ('specialist', 'Specialist Consultation'),
                    ('emergency', 'Emergency Visit'),
                    ('other', 'Other'),
                ],
                attrs={
                    'class': 'form-select'
                }
            ),
            'assessment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'completed_at': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'symptom_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'current_symptoms': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Current symptoms reported by the patient...'
            }),
            'previous_symptoms': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Previous symptoms that have resolved or changed...'
            }),
            'condition_progression': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'How the condition has progressed over time...'
            }),
            'pain_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'type': 'number',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'objective_findings': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 5,
                'placeholder': 'Objective clinical findings and observations...'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Treatment plan and recommendations...'
            }),
            'practitioner_notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Additional clinical notes...'
            }),
            'practitioner_notes_image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'capture': 'environment'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        clinician = kwargs.pop('clinician', None)
        super().__init__(*args, **kwargs)
        self.clinician = clinician
        
        # Determine if this is a physiotherapist
        is_physiotherapist = clinician and clinician.title == 'physiotherapist'
        
        if is_physiotherapist:
            # For physiotherapists, show all fields including subjective assessment
            # Set assessment_type to physiotherapy and disable it (value will be submitted via hidden input)
            self.fields['assessment_type'].initial = 'physiotherapy'
            self.fields['assessment_type'].widget.attrs['disabled'] = True
            self.fields['assessment_type'].widget.attrs['style'] = 'background-color: #f5f5f5; cursor: not-allowed;'
        else:
            # For other practitioners, hide subjective fields
            self.fields['current_symptoms'].widget = forms.HiddenInput()
            self.fields['previous_symptoms'].widget = forms.HiddenInput()
            self.fields['condition_progression'].widget = forms.HiddenInput()
            self.fields['pain_level'].widget = forms.HiddenInput()
            self.fields['symptom_date'].widget = forms.HiddenInput()
        
        # Make all fields optional - validation will be handled by JavaScript with user confirmation
        for field_name in self.fields:
            self.fields[field_name].required = False


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 'phone_number',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your phone number'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Emergency contact phone'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Spouse, Parent, Friend'
            }),
        }


class WorkHistoryForm(forms.ModelForm):
    """Form for adding/editing work history"""
    class Meta:
        from .models import WorkHistory
        model = WorkHistory
        fields = [
            'job_title', 'employer', 'start_date', 'end_date', 'is_current',
            'activities', 'hours_per_week', 'description', 'notes'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Job title or role'
            }),
            'employer': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Employer or company name'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'hours_per_week': forms.NumberInput(attrs={
                'class': 'form-input',
                'type': 'number',
                'min': '0',
                'max': '168',
                'placeholder': 'Hours per week'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Describe your work duties and environment...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Any additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        from .models import WorkHistory
        super().__init__(*args, **kwargs)
        # Create checkboxes for activities
        self.fields['activities'] = forms.MultipleChoiceField(
            choices=WorkHistory.ACTIVITY_CHOICES,
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'activity-checkboxes'
            }),
            required=False
        )

