from django.contrib import admin
from .models import Patient, Doctor, AdminUser, LoginRecord

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'phone', 'email', 'address')
    search_fields = ('username', 'phone', 'email')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'phone', 'email', 'address',
        'qualification', 'specialization', 'fees', 'photo'
    )
    search_fields = ('username', 'phone', 'email', 'specialization')

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('id',)
    # Add more fields here when AdminUser model is extended

@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'occupation', 'login_time', 'verified', 'device_ip')
    search_fields = ('user_id', 'username', 'occupation', 'device_ip')
