from users.models import UserProfile
from django.utils import timezone

# Create regular users
users_data = [
    {
        'username': 'Ayana',
        'first_name': 'Ayana',
        'last_name': 'Bakytzhanova',
        'email': 'ayana@example.com',
        'profile_photo': 'profile_photos/ayana.jpg',
        'is_staff': True,
        'is_active': True,
        'is_superuser': False,
    },
    {
        'username': 'Assem',
        'first_name': 'Assem',
        'last_name': 'Nagmetova',
        'email': 'assem@example.com',
        'profile_photo': 'profile_photos/assem.jpg',
        'is_staff': True,
        'is_active': True,
        'is_superuser': False,
    },
    {
        'username': 'Altush',
        'first_name': 'Altush',
        'last_name': 'Kabdygalieva',
        'email': 'altush@example.com',
        'profile_photo': 'profile_photos/altush.jpg',
        'is_staff': True,
        'is_active': True,
        'is_superuser': False,
    }
]

# Create users
for user_data in users_data:
    user, created = UserProfile.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'email': user_data['email'],
            'profile_photo': user_data['profile_photo'],
            'is_staff': user_data['is_staff'],
            'is_active': user_data['is_active'],
            'is_superuser': user_data['is_superuser'],
            'date_joined': timezone.now(),
        }
    )
    
    if created:
        # Set password for new users - same password for all
        user.set_password('IntGo12345')
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"User {user.username} already exists")

# Update admin password
try:
    admin = UserProfile.objects.get(username="admin")
    admin.set_password("IntGo12345")
    admin.save()
    print("Admin password updated to 'IntGo12345'")
except UserProfile.DoesNotExist:
    print("Admin user does not exist")