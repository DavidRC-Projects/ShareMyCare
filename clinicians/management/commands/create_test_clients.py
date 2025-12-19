from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clinicians.models import Clinician, PatientClinicianAccess
from accounts.models import UserProfile
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create 4 test client accounts and link them to clinician1'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test clients...'))
        
        # Find clinician1
        try:
            clinician_user = User.objects.get(username='clinician1')
            clinician = clinician_user.clinician_profile
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('clinician1 user not found. Please create it first.'))
            return
        except AttributeError:
            self.stdout.write(self.style.ERROR('clinician1 does not have a clinician profile. Please create it first.'))
            return
        
        # Test client data
        test_clients = [
            {
                'username': 'testclient1',
                'email': 'testclient1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
            },
            {
                'username': 'testclient2',
                'email': 'testclient2@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
            },
            {
                'username': 'testclient3',
                'email': 'testclient3@example.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
            },
            {
                'username': 'testclient4',
                'email': 'testclient4@example.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
            },
        ]
        
        created_count = 0
        linked_count = 0
        
        for client_data in test_clients:
            # Create or get user
            user, created = User.objects.get_or_create(
                username=client_data['username'],
                defaults={
                    'email': client_data['email'],
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                }
            )
            
            if created:
                # Set a default password
                user.set_password('testpass123')
                user.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {client_data["username"]}'))
            else:
                # Update existing user info
                user.email = client_data['email']
                user.first_name = client_data['first_name']
                user.last_name = client_data['last_name']
                user.save()
                self.stdout.write(self.style.WARNING(f'User already exists, updated: {client_data["username"]}'))
            
            # Create or get user profile
            profile, profile_created = UserProfile.objects.get_or_create(user=user)
            if profile_created:
                self.stdout.write(self.style.SUCCESS(f'Created profile for: {client_data["username"]}'))
            
            # Create or get PatientClinicianAccess
            access, access_created = PatientClinicianAccess.objects.get_or_create(
                patient=user,
                clinician=clinician,
                defaults={
                    'access_granted_by': user,
                    'is_active': True,
                    'access_level': 'full',
                }
            )
            
            if access_created:
                linked_count += 1
                self.stdout.write(self.style.SUCCESS(f'Linked {client_data["username"]} to clinician1'))
            else:
                # Update existing access to ensure it's active
                access.is_active = True
                access.save()
                self.stdout.write(self.style.WARNING(f'Access already exists for {client_data["username"]}, updated'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary:\n'
            f'  - Created {created_count} new users\n'
            f'  - Linked {linked_count} clients to clinician1\n'
            f'  - Total test clients: {len(test_clients)}\n'
            f'\nAll test clients have password: testpass123'
        ))

