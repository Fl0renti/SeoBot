from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Keyword, Profile
from .utils import search_google_for_keyword
from django.db import transaction
from django.contrib import messages


@receiver(post_save, sender=Order)
def search_on_order_creation(sender, instance, created, **kwargs):
    """
    Searches in google for that keyword whenever an order is created
    """
    if instance.click_domain_only:
        print("\n\nClicking Domain only\n\n")
        profile = Profile.objects.filter(domain_type=instance.domain_type).order_by('?').first()
        create_keyword(instance, profile)
    else:
        if created:
            print("Searching for: ", instance.domain_name, f'-- domain_type: {instance.domain_type}')
            search_google_for_keyword(instance)
            



def create_keyword(instance, profile):
    with transaction.atomic():
            keyword, created = Keyword.objects.get_or_create(
                id=instance.id,
                defaults={
                    'keyword': instance,
                    'profile': profile,
                    'status': "In Progress"
                }
            )
            if created:
                print("Keyword created:", keyword)
            else:
                print("Keyword already exists:", keyword)