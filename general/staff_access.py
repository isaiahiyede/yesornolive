from django.contrib.auth.models import User
from general.models import UserAccount

def staff_check_for_gameplay(user):
    if not user.is_staff:
        return True
    else:
        return False