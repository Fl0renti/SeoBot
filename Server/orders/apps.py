from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        try:
            from .tasks import set_all_profiles_unused
            import orders.signals
            set_all_profiles_unused()
        except:
            pass



    