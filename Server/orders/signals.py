from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils import search_google_for_keyword


@receiver(post_save, sender=Order)
def search_on_order_creation(sender, instance, created, **kwargs):
    """
    Searches in google for that keyword whenever an order is created
    """
    if created:
        print("Searching for: ", instance.domain_name, f'-- domain_type: {instance.domain_type}')
        search_google_for_keyword(instance)