import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

def check_and_fix_profiles():
    users = User.objects.all()
    print(f"Checking {users.count()} users...")
    
    for user in users:
        try:
            profile = user.profile
            print(f"User {user.username}: Profile exists. Balance: {profile.balance}")
        except Profile.DoesNotExist:
            print(f"User {user.username}: No profile found. Creating one...")
            Profile.objects.create(user=user)
            print(f"Created profile for {user.username}")
        except Exception as e:
            print(f"Error checking user {user.username}: {e}")

if __name__ == "__main__":
    check_and_fix_profiles()
