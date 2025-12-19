from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from health_records.models import Assessment, Medication, Condition, Allergy
from django.utils import timezone
from datetime import timedelta, date


class Command(BaseCommand):
    help = 'Add test data (assessments, medications, conditions) to 2 test clients to make them active'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding test data to clients...'))
        
        # Get the two test clients
        try:
            client1 = User.objects.get(username='testclient1')
            client2 = User.objects.get(username='testclient2')
        except User.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Test client not found: {e}'))
            return
        
        # Recent date (within last 30 days)
        recent_date = timezone.now() - timedelta(days=15)
        recent_date_only = recent_date.date()
        
        # Create assessments for client1
        assessment1 = Assessment.objects.create(
            user=client1,
            assessment_type='physiotherapy',
            assessment_date=recent_date_only,
            current_symptoms='Lower back pain, difficulty bending',
            pain_level=6,
            objective_findings='Reduced lumbar flexion, tight hamstrings',
            treatment_plan='Stretching exercises, core strengthening',
            created_at=recent_date
        )
        self.stdout.write(self.style.SUCCESS(f'Created assessment for {client1.username}'))
        
        # Create assessment for client2
        assessment2 = Assessment.objects.create(
            user=client2,
            assessment_type='general',
            assessment_date=recent_date_only,
            current_symptoms='Knee pain after running',
            pain_level=5,
            objective_findings='Mild swelling, reduced range of motion',
            treatment_plan='Rest, ice, compression, elevation',
            created_at=recent_date
        )
        self.stdout.write(self.style.SUCCESS(f'Created assessment for {client2.username}'))
        
        # Create medications for client1
        medication1 = Medication.objects.create(
            user=client1,
            name='Ibuprofen',
            dosage='400mg',
            frequency='Twice daily',
            start_date=recent_date_only - timedelta(days=5),
            is_active=True,
            is_prescribed=True,
            prescribing_clinician='Dr. Smith'
        )
        self.stdout.write(self.style.SUCCESS(f'Created medication for {client1.username}'))
        
        # Create medication for client2
        medication2 = Medication.objects.create(
            user=client2,
            name='Paracetamol',
            dosage='500mg',
            frequency='As needed',
            start_date=recent_date_only - timedelta(days=3),
            is_active=True,
            is_prescribed=True,
            prescribing_clinician='Dr. Johnson'
        )
        self.stdout.write(self.style.SUCCESS(f'Created medication for {client2.username}'))
        
        # Create conditions for client1
        condition1 = Condition.objects.create(
            user=client1,
            name='Lower Back Pain',
            diagnosis_date=recent_date_only - timedelta(days=20),
            status='active',
            notes='Chronic lower back pain, likely due to poor posture'
        )
        self.stdout.write(self.style.SUCCESS(f'Created condition for {client1.username}'))
        
        # Create condition for client2
        condition2 = Condition.objects.create(
            user=client2,
            name='Knee Injury',
            diagnosis_date=recent_date_only - timedelta(days=10),
            status='active',
            notes='Overuse injury from running'
        )
        self.stdout.write(self.style.SUCCESS(f'Created condition for {client2.username}'))
        
        # Create allergy for client1
        allergy1 = Allergy.objects.create(
            user=client1,
            allergen='Penicillin',
            severity='severe',
            reaction='Rash and difficulty breathing',
            date_identified=date(2020, 1, 15)
        )
        self.stdout.write(self.style.SUCCESS(f'Created allergy for {client1.username}'))
        
        # Create allergy for client2
        allergy2 = Allergy.objects.create(
            user=client2,
            allergen='Latex',
            severity='moderate',
            reaction='Skin irritation',
            date_identified=date(2019, 6, 10)
        )
        self.stdout.write(self.style.SUCCESS(f'Created allergy for {client2.username}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary:\n'
            f'  - Added 1 assessment to {client1.username}\n'
            f'  - Added 1 assessment to {client2.username}\n'
            f'  - Added 1 medication to each client\n'
            f'  - Added 1 condition to each client\n'
            f'  - Added 1 allergy to each client\n'
            f'\nBoth clients now have recent activity and should appear as "Active"'
        ))

