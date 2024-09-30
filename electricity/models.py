from django.db import models
from django.contrib.auth.models import User
# AbstractBaseUser, BaseUserManager
import random
from django.utils import timezone
# Create your models here.
from django_jsonform.models.fields import JSONField


class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    contact = models.CharField(max_length=15, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=100,null=True)
    state = models.CharField(max_length=100, null=True)
    regdate = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.user

class Connection(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    
    connectionid = models.BigIntegerField(primary_key=True, unique=True, editable=False)
    connectiontype = models.CharField(max_length=100, null=True)
    connectionstartdate = models.DateField(null=True)
    occupation = models.CharField(max_length=100, null=True)
    connectionload = models.CharField(max_length=100, null=True)
    plotno = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100, null=True)
    pincode = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=250, null=True)
    
    def save(self, *args, **kwargs):
        if not self.connectionid:
            self.connectionid = self.generate_unique_connectionid()
        super().save(*args, **kwargs)
    
    def generate_unique_connectionid(self):
        while True:
            connectionid = random.randint(1000000000, 9999999999)  # Generate a 10-digit number
            if not Connection.objects.filter(connectionid=connectionid).exists():
                return connectionid

    def __str__(self):
        return self.connectiontype


class Unitrate(models.Model):
    initialunit=models.FloatField(default=0.0)
    finalunit=models.FloatField(default=0.0)
    unitrate=models.FloatField(default=0.0)


class Bill(models.Model):
    connection = models.ForeignKey('Connection', on_delete=models.CASCADE)
    billformonth = models.DateField(default=timezone.now)
    currentreading = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    previousreading = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalunit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    chargeperunit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    finalamount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duedate = models.DateField(null=True)
    status = models.CharField(max_length=20, null=True)
    total_bill_amt=models.FloatField(default=0.0)
    current_bill_images=models.ImageField(upload_to='bills/', blank=True,null=True)
    def __str__(self):
        return self.status
    class Meta:
        unique_together = ('connection', 'billformonth')


class Bill_cal(models.Model):
    unit = models.FloatField(default=0.0)
    rate = models.FloatField(default=0.0)
    rate_details = models.CharField(max_length=10,null=True)
    amount = models.FloatField(default=0.0)
    total = models.ForeignKey(Bill ,on_delete=models.CASCADE)
    
class Bill_load(models.Model):
    load = models.FloatField(default=0.0)
    load_rate = models.FloatField(default=0.0)
    load_rate_details = models.CharField(max_length=10,null=True)
    load_amount = models.FloatField(default=0.0)
    load_total = models.ForeignKey(Bill ,on_delete=models.CASCADE) 
    
class Bill_fppas(models.Model):
    fppas = models.FloatField(default=0.0)
    fppas_rate = models.FloatField(default=0.0)
    fppas_rate_details = models.CharField(max_length=10,null=True)
    fppas_amount = models.FloatField(default=0.0)
    fppas_total = models.ForeignKey(Bill ,on_delete=models.CASCADE)
    
class Bill_cess(models.Model):
    cess = models.FloatField(default=0.0)
    cess_rate = models.FloatField(default=0.0)
    cess_rate_details = models.CharField(max_length=10,null=True)
    cess_amount = models.FloatField(default=0.0)
    cess_total = models.ForeignKey(Bill ,on_delete=models.CASCADE)            

class Bill_duty(models.Model):
    duty = models.FloatField(default=0.0)
    duty_rate = models.FloatField(default=0.0)
    duty_rate_details = models.CharField(max_length=10,null=True)
    duty_amount = models.FloatField(default=0.0)
    duty_total = models.ForeignKey(Bill ,on_delete=models.CASCADE)     

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)    

class ContactUs(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    message = models.TextField()

    
class Feedback(models.Model):
    SATISFACTION_CHOICES = [
        ('Very Satisfied', 'Very Satisfied'),
        ('Satisfied', 'Satisfied'),
        ('Neutral', 'Neutral'),
        ('Dissatisfied', 'Dissatisfied'),
        ('Very Dissatisfied', 'Very Dissatisfied'),
    ]
    
    EASE_OF_USE_CHOICES = [
        ('Very Easy', 'Very Easy'),
        ('Easy', 'Easy'),
        ('Neutral', 'Neutral'),
        ('Difficult', 'Difficult'),
        ('Very Difficult', 'Very Difficult'),
    ]
    
    CUSTOMER_SUPPORT_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Very Poor', 'Very Poor'),
    ]
    
    BILLING_PROCESS_CHOICES = [
        ('Very Satisfied', 'Very Satisfied'),
        ('Satisfied', 'Satisfied'),
        ('Neutral', 'Neutral'),
        ('Dissatisfied', 'Dissatisfied'),
        ('Very Dissatisfied', 'Very Dissatisfied'),
    ]

    satisfaction = models.CharField(max_length=50, choices=SATISFACTION_CHOICES)
    ease_of_use = models.CharField(max_length=50, choices=EASE_OF_USE_CHOICES)
    features_like = models.TextField(blank=True, null=True)
    additional_features = models.TextField(blank=True, null=True)
    customer_support = models.CharField(max_length=50, choices=CUSTOMER_SUPPORT_CHOICES)
    billing_process = models.CharField(max_length=50, choices=BILLING_PROCESS_CHOICES)
    improvement_suggestions = models.TextField(blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Feedback from {self.id}"
        
    
