from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_image_file


class Condition(models.Model):
    """Medical conditions/diagnoses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conditions')
    name = models.CharField(max_length=200)
    diagnosis_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('resolved', 'Resolved'),
            ('chronic', 'Chronic'),
            ('monitoring', 'Monitoring'),
        ],
        default='active'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-diagnosis_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Medication(models.Model):
    """Medications - both prescribed and non-prescribed"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)  # e.g., "twice daily", "as needed"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_prescribed = models.BooleanField(
        default=True,
        help_text="Whether this medication was prescribed by a healthcare provider"
    )
    prescribing_clinician = models.CharField(max_length=200, blank=True)
    prescription_image = models.ImageField(
        upload_to='prescriptions/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text="Photo of prescription if available"
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-start_date', '-created_at']

    def __str__(self):
        prescribed_status = "Prescribed" if self.is_prescribed else "Non-prescribed"
        return f"{self.user.username} - {self.name} ({prescribed_status})"


class Allergy(models.Model):
    """Allergies and adverse reactions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=200)  # Could be medication, food, environmental, etc.
    reaction = models.TextField(help_text="Description of the allergic reaction")
    severity = models.CharField(
        max_length=20,
        choices=[
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
            ('life_threatening', 'Life-threatening'),
        ],
        default='moderate'
    )
    date_identified = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-severity', '-date_identified']
        verbose_name_plural = 'Allergies'

    def __str__(self):
        return f"{self.user.username} - {self.allergen}"


class Assessment(models.Model):
    """Health assessments - combines user symptoms and practitioner objective assessments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    
    # User-entered symptom data
    current_symptoms = models.TextField(
        blank=True,
        help_text="Current symptoms described by the patient"
    )
    previous_symptoms = models.TextField(
        blank=True,
        help_text="Previous symptoms that have resolved or changed"
    )
    condition_progression = models.TextField(
        blank=True,
        help_text="How the condition has progressed over time"
    )
    pain_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Pain level from 0-10 (0 = no pain, 10 = worst pain)"
    )
    symptom_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when symptoms were recorded"
    )
    
    # Practitioner-entered objective assessment data
    clinician = models.ForeignKey(
        'clinicians.Clinician',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments',
        help_text="Clinician who added the objective assessment"
    )
    assessment_type = models.CharField(
        max_length=50,
        choices=[
            ('physiotherapy', 'Physiotherapy'),
            ('general', 'General Health Check'),
            ('specialist', 'Specialist Consultation'),
            ('emergency', 'Emergency Visit'),
            ('other', 'Other'),
        ],
        blank=True,
        help_text="Type of assessment (added by practitioner)"
    )
    assessment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the assessment (added by practitioner)"
    )
    objective_findings = models.TextField(
        blank=True,
        help_text="Objective clinical findings and observations (added by practitioner)"
    )
    treatment_plan = models.TextField(
        blank=True,
        help_text="Treatment plan (added by practitioner)"
    )
    practitioner_notes = models.TextField(
        blank=True,
        help_text="Additional notes from practitioner"
    )
    practitioner_notes_image = models.ImageField(
        upload_to='practitioner_notes/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text="Photo of practitioner's notes if available"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the assessment was completed by the practitioner"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assessment_date', '-symptom_date', '-created_at']

    def __str__(self):
        if self.assessment_date:
            return f"{self.user.username} - Assessment ({self.assessment_date})"
        elif self.symptom_date:
            return f"{self.user.username} - Symptoms ({self.symptom_date})"
        else:
            return f"{self.user.username} - Assessment Entry"
    
    @property
    def has_practitioner_data(self):
        """Check if practitioner has added objective assessment data"""
        return bool(self.clinician or self.objective_findings or self.treatment_plan)
    
    @property
    def has_user_symptoms(self):
        """Check if user has added symptom data"""
        return bool(self.current_symptoms or self.previous_symptoms or self.condition_progression or self.pain_level is not None)


class WorkHistory(models.Model):
    """Work history and occupational information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_history')
    
    # Work details
    job_title = models.CharField(max_length=200, help_text="Job title or role")
    employer = models.CharField(max_length=200, blank=True, help_text="Employer or company name")
    start_date = models.DateField(help_text="Start date of this work")
    end_date = models.DateField(null=True, blank=True, help_text="End date (leave blank if current job)")
    is_current = models.BooleanField(default=False, help_text="Is this your current job?")
    
    # Work activities
    ACTIVITY_CHOICES = [
        ('prolonged_sitting', 'Prolonged Sitting'),
        ('prolonged_standing', 'Prolonged Standing'),
        ('driving', 'Driving'),
        ('heavy_lifting', 'Heavy Lifting'),
        ('repetitive_movements', 'Repetitive Movements'),
        ('computer_work', 'Computer Work'),
        ('manual_labor', 'Manual Labor'),
        ('walking', 'Walking'),
        ('climbing', 'Climbing'),
        ('bending', 'Bending/Twisting'),
        ('vibration', 'Vibration Exposure'),
        ('other', 'Other'),
    ]
    
    activities = models.JSONField(
        default=list,
        help_text="List of work activities (selected from choices)"
    )
    
    hours_per_week = models.IntegerField(
        null=True,
        blank=True,
        help_text="Average hours worked per week"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Additional details about work duties and environment"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Any additional notes about this work history"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_current', '-start_date']
        verbose_name_plural = 'Work Histories'

    def __str__(self):
        status = "Current" if self.is_current else "Previous"
        return f"{self.user.username} - {self.job_title} ({status})"
    
    def get_activities_display(self):
        """Return human-readable activity names"""
        activity_dict = dict(self.ACTIVITY_CHOICES)
        return [activity_dict.get(activity, activity) for activity in self.activities]


class ExtractedFindings(models.Model):
    """Extracted findings from therapist notes using Azure Document Intelligence"""
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='extracted_findings',
        help_text="Assessment this finding belongs to"
    )
    
    # Finding details
    category = models.CharField(
        max_length=50,
        choices=[
            ('assessment', 'Assessment'),
            ('diagnosis', 'Diagnosis'),
            ('treatment', 'Treatment'),
            ('prognosis', 'Prognosis'),
            ('recommendations', 'Recommendations'),
            ('measurements', 'Measurements'),
            ('symptoms', 'Symptoms'),
            ('general', 'General'),
        ],
        default='general',
        help_text="Category of the finding"
    )
    
    finding_type = models.CharField(
        max_length=50,
        choices=[
            ('measurement', 'Measurement'),
            ('strength', 'Strength'),
            ('symptom', 'Symptom'),
            ('treatment', 'Treatment'),
            ('observation', 'Observation'),
        ],
        default='observation',
        help_text="Type of finding"
    )
    
    text = models.TextField(
        help_text="Extracted text of the finding"
    )
    
    # Metadata
    raw_extraction_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Raw data from Azure Document Intelligence"
    )
    
    extracted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the finding was extracted"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the finding has been verified by a clinician"
    )
    
    verified_by = models.ForeignKey(
        'clinicians.Clinician',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_findings',
        help_text="Clinician who verified this finding"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the finding was verified"
    )
    
    class Meta:
        ordering = ['-extracted_at', 'category']
        verbose_name_plural = 'Extracted Findings'
    
    def __str__(self):
        return f"Finding: {self.text[:50]}... ({self.get_category_display()})"
