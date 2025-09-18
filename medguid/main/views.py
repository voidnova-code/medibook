from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Patient, Doctor, LoginRecord
import random
import string
from twilio.rest import Client
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def generate_otp(length=6):
    """Generate a numeric OTP of given length."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp(phone, otp):
    # Use Twilio to send SMS
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    if not all([account_sid, auth_token, twilio_number]):
        print("Twilio credentials are not set in settings.")
        return
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=f"Your Medibook OTP is: {otp}",
            from_=twilio_number,
            to=f"+91{phone}"
        )
        print(f"OTP sent to {phone}: {otp}")
    except Exception as e:
        print(f"Failed to send OTP via Twilio: {e}")

def verify_otp(input_otp, session_otp):
    """Return True if OTP matches, else False."""
    return input_otp == session_otp

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        otp = request.POST.get('otp')
        action = request.POST.get('action')
        user = None
        phone = None
        username = None
        user_type = None

        # Check if user exists in Patient or Doctor using user_id
        try:
            user = Patient.objects.get(id=user_id)
            phone = user.phone
            username = user.username
            user_type = 'patient'
        except Patient.DoesNotExist:
            try:
                user = Doctor.objects.get(id=user_id)
                phone = user.phone
                username = user.username
                user_type = 'doctor'
            except Doctor.DoesNotExist:
                user = None

        device_ip = request.META.get('REMOTE_ADDR', '')

        if not user:
            LoginRecord.objects.create(
                user_id=user_id,
                username='Unknown',
                occupation='Unknown',
                verified=False,
                device_ip=device_ip
            )
            messages.error(request, 'User does not exist.')
            return render(request, 'login.html')

        if action == "send_otp":
            generated_otp = generate_otp()
            request.session['login_otp'] = generated_otp
            request.session['login_user_id'] = user_id
            send_otp(phone, generated_otp)
            messages.info(request, f"OTP sent to your registered phone number ending with {phone[-4:]}")
            return render(request, 'login.html', {'user_id': user_id})

        if action == "login":
            session_otp = request.session.get('login_otp')
            session_user_id = request.session.get('login_user_id')
            verified = verify_otp(otp, session_otp) and user_id == session_user_id
            LoginRecord.objects.create(
                user_id=user_id,
                username=username,
                occupation=user_type,
                verified=verified,
                device_ip=device_ip
            )
            if verified:
                # Clear OTP from session
                request.session.pop('login_otp', None)
                request.session.pop('login_user_id', None)
                return redirect('home')
            else:
                messages.error(request, 'OTP not matched.')
                return render(request, 'login.html', {'user_id': user_id})

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def generate_user_id(phone):
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{letters}{phone}"

def signup_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'patient':
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address = request.POST.get('address')
            if username and phone and email and address:
                user_id = generate_user_id(phone)
                Patient.objects.create(
                    id=user_id,
                    username=username,
                    phone=phone,
                    email=email,
                    address=address
                )
                messages.success(request, f"Your User ID is: {user_id}. Please memorize or save this User ID for future logins.")
                return redirect('home')
            else:
                messages.error(request, "All patient fields are required.")
                return render(request, 'signup.html')
        elif user_type == 'doctor':
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address = request.POST.get('address')
            qualification = request.POST.get('qualification')
            specialization = request.POST.get('specialization')
            fees = request.POST.get('fees')
            photo = request.FILES.get('photo')
            if all([username, phone, email, address, qualification, specialization, fees, photo]):
                user_id = generate_user_id(phone)
                doctor = Doctor(
                    id=user_id,
                    username=username,
                    phone=phone,
                    email=email,
                    address=address,
                    qualification=qualification,
                    specialization=specialization,
                    fees=fees
                )
                doctor.save()  # Save without photo first
                doctor.photo = photo  # Assign photo after ID is set
                doctor.save()  # Save again to trigger correct upload_to
                messages.success(request, f"Your User ID is: {user_id}. Please memorize or save this User ID for future logins.")
                return redirect('home')
            else:
                messages.error(request, "All doctor fields are required.")
                return render(request, 'signup.html')
        # Admin logic can be added later
        return redirect('index')
    return render(request, 'signup.html')

def logout_view(request):
    # Optionally clear session data if needed
    request.session.flush()
    return redirect('index')

# Create your views here.
