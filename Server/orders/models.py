from django.db import models
from django.urls import reverse
from django.utils import timezone


class Order(models.Model):
    DOMAIN_TYPE_CHOICES = [
        ('web', 'Web'),
        ('mobile', 'Mobile'),
    ]
    ACTION_CHOICES = [
        ("Sponsored", "Sponsored"),
        ("Business", "Business"),
        ("Sponsored Business", "Sponsored Business"),
    ]
    SECOND_ACTION_CHOICES = [
        ('website', 'Website'),
        ('direction', 'Direction'),
        ('call', 'Call'),
    ]
    domain_name = models.CharField(max_length=100)
    active = models.BooleanField(default=False, verbose_name='Active')
    work_sec = models.PositiveIntegerField(verbose_name="Work Seconds", default=30, help_text="Minimum 30 seconds")
    avg_sec = models.PositiveIntegerField(verbose_name="Average Seconds", default=30, help_text="Minimum 30 seconds")
    num_users = models.PositiveIntegerField(verbose_name="Number of Users")
    reached_users = models.PositiveIntegerField(verbose_name="Reached Users", default=0)
    order_schedule = models.DateTimeField(verbose_name="Order Schedule", null=True, blank=True)
    domain_type = models.CharField(max_length=10, choices=DOMAIN_TYPE_CHOICES, default='web', verbose_name='Domain Type')

    action = models.CharField(max_length=100, null=True, blank=True, choices=ACTION_CHOICES)
    second_action = models.CharField(max_length=10, choices=SECOND_ACTION_CHOICES, null=True, blank=True)
    

    def WorkerRequired(self):
        return int(self.num_users - self.reached_users)

    def __str__(self):
        return f"Order {self.domain_name}"
    
    def get_absolute_url(self):
        return reverse("orders:list_of_orders")

    class Meta:
        db_table = 'orders'

class Keyword(models.Model):
    
    keyword = models.ForeignKey(Order, on_delete=models.CASCADE)
    has_sponsored = models.BooleanField(default=False)
    has_business = models.BooleanField(default=False)
    has_sponsored_business = models.BooleanField(default=False)

    profile = models.ForeignKey("Profile", on_delete=models.CASCADE) #Profili kur t ruhet e mer njo random prej profilave.
    status = models.CharField(max_length=100, choices=[("Waiting", "Waiting"), ("In Progress", "In Progress"), ("Done", "Done")], default="Waiting") #Fillimisht e ka waiting, masnej e ka 1 template te ri useri ku i sheh veq waiting edhe ai masnej e plotson edhe 1 her orderin

    def __str__(self) -> str:
        return str(self.keyword.domain_name)
    
    def update_status(self, sponsored, business, sponsored_business, profile):
        self.has_sponsored = sponsored
        self.has_business = business
        self.has_sponsored_business = sponsored_business
        self.profile = profile
        self.status = "Done"
        self.save()

    def __str__(self) -> str:
        return str(self.keyword.domain_name)


class ServerTable(models.Model):
    name = models.CharField(max_length = 255)

    def __str__(self):
        return self.name

class Profile(models.Model):
    DOMAIN_TYPE_CHOICES = [
        ('web', 'Web'),
        ('mobile', 'Mobile'),
    ]
    proxy= models.CharField(max_length = 255)
    UserAgent = models.CharField(max_length = 255)
    domain_type = models.CharField(max_length=10, choices=DOMAIN_TYPE_CHOICES, default='web', verbose_name='Domain Type')
    serverID = models.ForeignKey(ServerTable,on_delete=models.CASCADE,null=True,blank=True)
    inUsed = models.BooleanField(default = False)
    last_fetched = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.proxy+ " - " + self.domain_type +" - " + str(self.inUsed)
    
    def get_absolute_url(self):
        return reverse('profile')

    def reset_in_used(self):
        self.inUsed = False
        self.save()
    
class ProxyDetail(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    status = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    countryCode = models.CharField(max_length=10)
    region = models.CharField(max_length=100)
    regionName = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    lat = models.FloatField()
    lon = models.FloatField()
    timezone = models.CharField(max_length=100)
    query = models.CharField(max_length=200)  # Assuming this is the IP or similar identifier
    proxyusername = models.CharField(max_length=100, null=True, blank=True)
    proxy_password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.profile}"