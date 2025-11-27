from django.db import models
from django.contrib.auth.models import User


class Clinician(models.Model):
    """Clinician profile and information"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='clinician_profile',
        null=True,
        blank=True,
        help_text="Link to a User account if the clinician has login access"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(
        max_length=50,
        choices=[
            ('dr', 'Dr.'),
            ('nurse', 'Nurse'),
            ('physiotherapist', 'Physiotherapist'),
            ('paramedic', 'Paramedic'),
            ('specialist', 'Specialist'),
            ('other', 'Other'),
        ],
        default='dr'
    )
    registration_number = models.CharField(max_length=100, blank=True)
    speciality = models.CharField(max_length=200, blank=True)
    organisation = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_title_display()} {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PatientClinicianAccess(models.Model):
    """Manages which clinicians have access to which patients' records"""
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clinician_accesses',
        help_text="The patient whose records are being shared"
    )
    clinician = models.ForeignKey(
        Clinician,
        on_delete=models.CASCADE,
        related_name='patient_accesses',
        help_text="The clinician who has access"
    )
    access_granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_accesses',
        help_text="The user who granted this access (usually the patient or their family member)"
    )
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Access'),
            ('read_only', 'Read Only'),
            ('emergency', 'Emergency Only'),
        ],
        default='read_only'
    )
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date for temporary access")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-granted_at']
        unique_together = ['patient', 'clinician']
        verbose_name_plural = 'Patient Clinician Accesses'

    def __str__(self):
        return f"{self.patient.username} -> {self.clinician.full_name} ({self.access_level})"


class FamilyMemberAccess(models.Model):
    """Manages family member/caregiver access to patient records"""
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='family_accesses',
        help_text="The patient whose records are being shared"
    )
    family_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='family_member_accesses',
        help_text="The family member/caregiver who has access"
    )
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('spouse', 'Spouse/Partner'),
            ('parent', 'Parent'),
            ('child', 'Child'),
            ('sibling', 'Sibling'),
            ('caregiver', 'Caregiver'),
            ('other', 'Other'),
        ]
    )
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Access'),
            ('read_only', 'Read Only'),
            ('emergency', 'Emergency Only'),
        ],
        default='read_only'
    )
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date for temporary access")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-granted_at']
        unique_together = ['patient', 'family_member']
        verbose_name_plural = 'Family Member Accesses'

    def __str__(self):
        return f"{self.patient.username} -> {self.family_member.username} ({self.relationship})"
