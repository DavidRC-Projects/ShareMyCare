from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string
from django.utils import timezone


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
    registration_body = models.CharField(
        max_length=20,
        choices=[
            ('GMC', 'GMC - General Medical Council'),
            ('NMC', 'NMC - Nursing and Midwifery Council'),
            ('HCPC', 'HCPC - Health and Care Professions Council'),
            ('other', 'Other'),
        ],
        blank=True,
        null=True,
        help_text="Professional registration body"
    )
    registration_verified = models.BooleanField(
        default=False,
        help_text="Whether the registration number has been verified"
    )
    registration_verified_at = models.DateTimeField(null=True, blank=True)
    registration_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_registrations',
        help_text="User who verified the registration"
    )
    speciality = models.CharField(max_length=200, blank=True)
    organisation = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    practitioner_code = models.CharField(
        max_length=5,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text="Unique 5-character alphanumeric code for patients to find this practitioner"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_title_display()} {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @staticmethod
    def generate_unique_code():
        """Generate a unique 5-character alphanumeric code"""
        while True:
            # Generate a random 5-character code (uppercase letters and digits)
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            # Check if code already exists
            if not Clinician.objects.filter(practitioner_code=code).exists():
                return code
    
    def save(self, *args, **kwargs):
        # Generate code only if it doesn't exist (new clinician)
        if not self.practitioner_code:
            self.practitioner_code = Clinician.generate_unique_code()
        super().save(*args, **kwargs)


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
    
    # Consent fields for specific record types (all default to True - patient can uncheck)
    consent_medications = models.BooleanField(default=True, help_text="Consent to share medications")
    consent_conditions = models.BooleanField(default=True, help_text="Consent to share conditions")
    consent_allergies = models.BooleanField(default=True, help_text="Consent to share allergies")
    consent_symptoms = models.BooleanField(default=True, help_text="Consent to share symptoms/assessments")
    consent_personal_info = models.BooleanField(default=True, help_text="Consent to share personal information")
    consent_emergency_contacts = models.BooleanField(default=True, help_text="Consent to share emergency contacts")
    consent_work_history = models.BooleanField(default=True, help_text="Consent to share work history")
    consent_feedback = models.BooleanField(default=True, help_text="Consent to share healthcare feedback")
    consent_given_at = models.DateTimeField(null=True, blank=True, help_text="When consent was given")

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


class HealthcareFeedback(models.Model):
    """Private feedback about healthcare organisations (not individual HCPs)"""
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='healthcare_feedback',
        help_text="The patient providing feedback"
    )
    organisation = models.CharField(
        max_length=200,
        help_text="The healthcare organisation (not individual HCP name)"
    )
    access = models.ForeignKey(
        PatientClinicianAccess,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback',
        help_text="Link to the access record (optional, for context)"
    )
    
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Overall rating (1-5)"
    )
    
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('communication', 'Communication'),
            ('care_quality', 'Quality of Care'),
            ('waiting_time', 'Waiting Times'),
            ('facilities', 'Facilities'),
            ('overall', 'Overall Experience'),
            ('other', 'Other'),
        ],
        default='overall'
    )
    
    feedback_text = models.TextField(
        help_text="Your feedback (constructive and respectful)"
    )
    
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Submit feedback anonymously (your name will not be shared)"
    )
    
    is_private = models.BooleanField(
        default=True,
        help_text="Keep feedback private (only visible to you and the organisation)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Healthcare Feedback'
    
    def __str__(self):
        return f"Feedback for {self.organisation} by {self.patient.username if not self.is_anonymous else 'Anonymous'}"


class ClinicianInvitation(models.Model):
    """Invitation for a clinician to join and access a patient's records"""
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clinician_invitations',
        help_text="The patient inviting the clinician"
    )
    email = models.EmailField(help_text="Email address of the clinician to invite")
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Optional message from patient")
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['patient', 'email']
    
    def __str__(self):
        return f"Invitation for {self.email} from {self.patient.username}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        return not self.is_accepted and not self.is_expired()


class ObjectiveMeasures(models.Model):
    """Objective measures including joint ROM and power assessments"""
    assessment = models.OneToOneField(
        'health_records.Assessment',
        on_delete=models.CASCADE,
        related_name='objective_measures',
        help_text="Link to the assessment this objective data belongs to"
    )
    clinician = models.ForeignKey(
        Clinician,
        on_delete=models.CASCADE,
        related_name='objective_measures',
        help_text="Clinician who performed the assessment"
    )
    assessment_date = models.DateField(help_text="Date of the objective assessment")
    
    # Joint ROM (Range of Motion) - All major joints
    # Upper Extremity
    shoulder_rom_left = models.CharField(max_length=200, blank=True, help_text="Left shoulder ROM")
    shoulder_rom_right = models.CharField(max_length=200, blank=True, help_text="Right shoulder ROM")
    elbow_rom_left = models.CharField(max_length=200, blank=True, help_text="Left elbow ROM")
    elbow_rom_right = models.CharField(max_length=200, blank=True, help_text="Right elbow ROM")
    wrist_rom_left = models.CharField(max_length=200, blank=True, help_text="Left wrist ROM")
    wrist_rom_right = models.CharField(max_length=200, blank=True, help_text="Right wrist ROM")
    hand_rom_left = models.CharField(max_length=200, blank=True, help_text="Left hand ROM")
    hand_rom_right = models.CharField(max_length=200, blank=True, help_text="Right hand ROM")
    
    # Lower Extremity
    hip_rom_left = models.CharField(max_length=200, blank=True, help_text="Left hip ROM")
    hip_rom_right = models.CharField(max_length=200, blank=True, help_text="Right hip ROM")
    knee_rom_left = models.CharField(max_length=200, blank=True, help_text="Left knee ROM")
    knee_rom_right = models.CharField(max_length=200, blank=True, help_text="Right knee ROM")
    ankle_rom_left = models.CharField(max_length=200, blank=True, help_text="Left ankle ROM")
    ankle_rom_right = models.CharField(max_length=200, blank=True, help_text="Right ankle ROM")
    foot_rom_left = models.CharField(max_length=200, blank=True, help_text="Left foot ROM")
    foot_rom_right = models.CharField(max_length=200, blank=True, help_text="Right foot ROM")
    
    # Spine
    cervical_rom = models.CharField(max_length=200, blank=True, help_text="Cervical spine ROM")
    thoracic_rom = models.CharField(max_length=200, blank=True, help_text="Thoracic spine ROM")
    lumbar_rom = models.CharField(max_length=200, blank=True, help_text="Lumbar spine ROM")
    
    # Power/Strength - All major muscle groups
    # Upper Extremity Power
    shoulder_power_left = models.CharField(max_length=200, blank=True, help_text="Left shoulder power")
    shoulder_power_right = models.CharField(max_length=200, blank=True, help_text="Right shoulder power")
    elbow_power_left = models.CharField(max_length=200, blank=True, help_text="Left elbow power")
    elbow_power_right = models.CharField(max_length=200, blank=True, help_text="Right elbow power")
    wrist_power_left = models.CharField(max_length=200, blank=True, help_text="Left wrist power")
    wrist_power_right = models.CharField(max_length=200, blank=True, help_text="Right wrist power")
    grip_power_left = models.CharField(max_length=200, blank=True, help_text="Left grip power")
    grip_power_right = models.CharField(max_length=200, blank=True, help_text="Right grip power")
    
    # Lower Extremity Power
    hip_power_left = models.CharField(max_length=200, blank=True, help_text="Left hip power")
    hip_power_right = models.CharField(max_length=200, blank=True, help_text="Right hip power")
    knee_power_left = models.CharField(max_length=200, blank=True, help_text="Left knee power")
    knee_power_right = models.CharField(max_length=200, blank=True, help_text="Right knee power")
    ankle_power_left = models.CharField(max_length=200, blank=True, help_text="Left ankle power")
    ankle_power_right = models.CharField(max_length=200, blank=True, help_text="Right ankle power")
    
    # Core/Trunk
    core_power = models.CharField(max_length=200, blank=True, help_text="Core/trunk power")
    
    # Additional notes
    additional_notes = models.TextField(blank=True, help_text="Additional objective findings")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessment_date', '-created_at']
        verbose_name_plural = 'Objective Measures'
    
    def __str__(self):
        return f"Objective Measures for {self.assessment.user.username} - {self.assessment_date}"
