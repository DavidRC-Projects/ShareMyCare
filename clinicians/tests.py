from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.mail import outbox
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from .models import Clinician, PatientClinicianAccess
from health_records.models import Assessment


class ClinicianModelTests(TestCase):
    """Test Clinician model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testclinician',
            email='clinician@test.com',
            password='testpass123'
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            title='dr',
            email='clinician@test.com',
            organisation='Test Hospital'
        )
    
    def test_clinician_creation(self):
        """Test that clinician is created with practitioner code"""
        self.assertIsNotNone(self.clinician.practitioner_code)
        self.assertEqual(len(self.clinician.practitioner_code), 5)
        self.assertTrue(self.clinician.practitioner_code.isalnum())
    
    def test_clinician_full_name(self):
        """Test full_name property"""
        self.assertEqual(self.clinician.full_name, 'John Doe')
    
    def test_practitioner_code_uniqueness(self):
        """Test that practitioner codes are unique"""
        clinician2 = Clinician.objects.create(
            first_name='Jane',
            last_name='Smith',
            title='nurse',
            email='jane@test.com'
        )
        self.assertNotEqual(self.clinician.practitioner_code, clinician2.practitioner_code)


class SendPractitionerCodeEmailTests(TestCase):
    """Test sending practitioner code by email"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testclinician',
            email='clinician@test.com',
            password='testpass123'
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            title='dr',
            email='clinician@test.com',
            organisation='Test Hospital'
        )
        self.client.login(username='testclinician', password='testpass123')
    
    def test_send_code_requires_login(self):
        """Test that sending code requires authentication"""
        self.client.logout()
        response = self.client.post(reverse('clinicians:send_practitioner_code_email'), {
            'client_email': 'client@test.com'
        })
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
    
    def test_send_code_requires_clinician(self):
        """Test that only clinicians can send codes"""
        regular_user = User.objects.create_user(
            username='regularuser',
            email='user@test.com',
            password='testpass123'
        )
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.post(reverse('clinicians:send_practitioner_code_email'), {
            'client_email': 'client@test.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
    
    def test_send_code_requires_email(self):
        """Test that email address is required"""
        response = self.client.post(reverse('clinicians:send_practitioner_code_email'), {
            'client_email': ''
        })
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_send_code_validates_email_format(self):
        """Test that email format is validated"""
        response = self.client.post(
            reverse('clinicians:send_practitioner_code_email'),
            {'client_email': 'invalid-email'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('valid email', data['message'].lower())
    
    def test_send_code_success(self):
        """Test successful email sending"""
        from django.core import mail
        response = self.client.post(
            reverse('clinicians:send_practitioner_code_email'),
            {'client_email': 'client@test.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.clinician.practitioner_code, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['client@test.com'])
    
    def test_send_code_without_practitioner_code(self):
        """Test error when practitioner code is missing"""
        # The model's save() method auto-generates codes, so we need to bypass it
        # by using update() which doesn't call save()
        Clinician.objects.filter(pk=self.clinician.pk).update(practitioner_code=None)
        # Refresh from database
        self.clinician.refresh_from_db()
        # Verify it's None
        self.assertIsNone(self.clinician.practitioner_code)
        
        response = self.client.post(
            reverse('clinicians:send_practitioner_code_email'),
            {'client_email': 'client@test.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')


class PractitionerDashboardTests(TestCase):
    """Test practitioner dashboard"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testclinician',
            email='clinician@test.com',
            password='testpass123'
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            title='dr',
            email='clinician@test.com'
        )
        self.client.login(username='testclinician', password='testpass123')
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('clinicians:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_requires_clinician(self):
        """Test that dashboard requires clinician profile"""
        regular_user = User.objects.create_user(
            username='regularuser',
            email='user@test.com',
            password='testpass123'
        )
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.get(reverse('clinicians:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_dashboard_displays_practitioner_code(self):
        """Test that dashboard displays practitioner code"""
        response = self.client.get(reverse('clinicians:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.clinician.practitioner_code)


class ClientAccessTests(TestCase):
    """Test client access functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.clinician_user = User.objects.create_user(
            username='testclinician',
            email='clinician@test.com',
            password='testpass123'
        )
        self.clinician = Clinician.objects.create(
            user=self.clinician_user,
            first_name='John',
            last_name='Doe',
            title='dr',
            email='clinician@test.com'
        )
        self.patient_user = User.objects.create_user(
            username='testpatient',
            email='patient@test.com',
            password='testpass123'
        )
        self.client.login(username='testclinician', password='testpass123')
    
    def test_clinician_can_view_own_clients(self):
        """Test that clinician can view their clients"""
        # Create access relationship
        PatientClinicianAccess.objects.create(
            patient=self.patient_user,
            clinician=self.clinician,
            is_active=True
        )
        response = self.client.get(reverse('clinicians:clients_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient_user.username)
    
    def test_clinician_cannot_view_other_clinicians_clients(self):
        """Test that clinician cannot view other clinicians' clients"""
        other_clinician = Clinician.objects.create(
            first_name='Jane',
            last_name='Smith',
            title='nurse',
            email='jane@test.com'
        )
        other_patient = User.objects.create_user(
            username='otherpatient',
            email='other@test.com',
            password='testpass123'
        )
        PatientClinicianAccess.objects.create(
            patient=other_patient,
            clinician=other_clinician,
            is_active=True
        )
        response = self.client.get(reverse('clinicians:clients_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_patient.username)
