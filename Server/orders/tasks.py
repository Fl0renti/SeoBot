# tasks.py

from .models import Profile




def set_all_profiles_unused():
    """
    Whenever the server restarts, all profiles are set to unused.
    Profiles are carefully checked again if they are being already used from views and Bot.
    """
    Profile.objects.update(inUsed=False)
    print('\n--All profiles have been set to unused--\n')
