from django.db import models
import uuid

def generate_random_id():
    return uuid.uuid4().hex  # 32-character random string

class Patient(models.Model):
    id = models.CharField(primary_key=True, max_length=23, editable=False)  # 3 letters + up to 20 digits
    username = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

def doctor_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'doctor_photos/{instance.id}.{ext}'

class Doctor(models.Model):
    id = models.CharField(primary_key=True, max_length=23, editable=False)  # 3 letters + up to 20 digits
    username = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to=doctor_photo_upload_path)

class AdminUser(models.Model):
    # Placeholder for future admin fields
    pass

class LoginRecord(models.Model):
    user_id = models.CharField(max_length=23)
    username = models.CharField(max_length=150)
    occupation = models.CharField(max_length=20, default='Unknown', blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    device_ip = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user_id} ({self.username}) [{self.occupation}] at {self.login_time} - {'Verified' if self.verified else 'Not Verified'}"
