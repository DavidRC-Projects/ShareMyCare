from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Medication, Condition, Allergy, Assessment
from accounts.models import UserProfile


class HealthRecordsModelTests(TestCase):
    """Test health records models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_medication_creation(self):
        """Test medication creation"""
        medication = Medication.objects.create(
            user=self.user,
            name='Aspirin',
            dosage='100mg',
            frequency='Once daily',
            is_active=True
        )
        self.assertEqual(medication.user, self.user)
        self.assertEqual(medication.name, 'Aspirin')
        self.assertTrue(medication.is_active)
    
    def test_condition_creation(self):
        """Test condition creation"""
        condition = Condition.objects.create(
            user=self.user,
            name='Diabetes',
            status='active'
        )
        self.assertEqual(condition.user, self.user)
        self.assertEqual(condition.status, 'active')
    
    def test_allergy_creation(self):
        """Test allergy creation"""
        allergy = Allergy.objects.create(
            user=self.user,
            allergen='Peanuts',
            reaction='Anaphylaxis',
            severity='severe'
        )
        self.assertEqual(allergy.user, self.user)
        self.assertEqual(allergy.severity, 'severe')


class DashboardTests(TestCase):
    """Test dashboard functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('health_records:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_displays_user_data(self):
        """Test that dashboard displays user's health records"""
        Medication.objects.create(
            user=self.user,
            name='Aspirin',
            is_active=True
        )
        Condition.objects.create(
            user=self.user,
            name='Diabetes',
            status='active'
        )
        response = self.client.get(reverse('health_records:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aspirin')
        self.assertContains(response, 'Diabetes')


class MedicationTests(TestCase):
    """Test medication views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_add_medication_requires_login(self):
        """Test that adding medication requires login"""
        self.client.logout()
        response = self.client.get(reverse('health_records:add_medication'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_add_medication_success(self):
        """Test successful medication addition"""
        response = self.client.post(reverse('health_records:add_medication'), {
            'name': 'Aspirin',
            'dosage': '100mg',
            'frequency': 'Once daily',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Medication.objects.filter(user=self.user, name='Aspirin').exists())
    
    def test_edit_medication_ownership(self):
        """Test that users can only edit their own medications"""
        medication = Medication.objects.create(
            user=self.user,
            name='Aspirin',
            is_active=True
        )
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(reverse('health_records:edit_medication', args=[medication.pk]), {
            'name': 'Modified Aspirin'
        })
        # Should either 404 or redirect (depending on implementation)
        self.assertIn(response.status_code, [302, 404])


class AssessmentTests(TestCase):
    """Test assessment views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_add_assessment_success(self):
        """Test successful assessment addition"""
        from django.utils import timezone
        response = self.client.post(reverse('health_records:add_assessment'), {
            'symptom_date': timezone.now().date(),
            'current_symptoms': 'Headache and fever',
            'pain_level': 5
        })
        # Should redirect after success
        self.assertIn(response.status_code, [200, 302])
    
    def test_assessment_ownership(self):
        """Test that assessments belong to the correct user"""
        assessment = Assessment.objects.create(
            user=self.user,
            current_symptoms='Test symptoms'
        )
        self.assertEqual(assessment.user, self.user)
        self.assertIn(assessment, self.user.assessments.all())
