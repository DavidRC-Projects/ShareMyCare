from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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
    """Health assessments - can be physiotherapy, general health checks, etc."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(
        max_length=50,
        choices=[
            ('physiotherapy', 'Physiotherapy'),
            ('general', 'General Health Check'),
            ('specialist', 'Specialist Consultation'),
            ('emergency', 'Emergency Visit'),
            ('other', 'Other'),
        ],
        default='general'
    )
    date = models.DateField()
    clinician_name = models.CharField(max_length=200, blank=True)
    findings = models.TextField(help_text="Clinical findings and observations")
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.assessment_type} ({self.date})"
