import random
from django.shortcuts import render, redirect
from . import forms
from .forms import ChangeUserForm
from django.contrib.auth.forms import  AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login , update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
# from car.models import Car
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.conf import settings
from accounts.models import Profile
from django.views.generic import FormView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from .models import UserOTP
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth.models import User
from .forms import RegistrationForm
from django import forms
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from posts.models import Post

def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}.'
    from_email = 'ratulhasan2108@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    
class UserLoginView(LoginView):
    template_name = 'user_login.html'
    
    def get_success_url(self):
        return reverse_lazy('otp_verify')
    
    def form_valid(self, form):
        user = form.get_user()
        otp = random.randint(100000, 999999)
        UserOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp, 'created_at': timezone.now()}
        )
        send_otp_via_email(user.email, otp)  # Implement this function to send OTP via email
        self.request.session['otp_user_id'] = user.id
        messages.success(self.request, 'An OTP has been sent to your email.')
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        messages.error(self.request, 'Login information incorrect')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Login'
        return context


class UserRegistrationView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('homepage')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        user=form.save()
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        messages.success(self.request, 'Please confirm your email address to complete the registration')
        return super().form_valid(form)
    
# class UserRegistrationView(FormView):
#     template_name = 'register.html'
#     form_class = RegistrationForm
#     success_url = reverse_lazy('profile')
    
#     def form_valid(self,form):
#         print(form.cleaned_data)
#         user = form.save()
#         login(self.request, user)
#         print(user)
#         return super().form_valid(form)
        
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully')
        return redirect('profile')
    else:
        messages.warning(request, 'Activation link is invalid!')
        return redirect('register')



class UserProfileUpdateView(View):
    template_name = 'edit_profile.html'

    def get(self, request):
        user = request.user
        profile = user.profile
        form = ChangeUserForm(instance=user, initial={
            'address': profile.address,
            'contact_number': profile.contact_number,
            'designation': profile.designation,
            'dept': profile.dept,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user = request.user
        profile = user.profile
        form = ChangeUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            profile.address = form.cleaned_data['address']
            profile.contact_number = form.cleaned_data['contact_number']
            profile.designation = form.cleaned_data['designation']
            profile.dept = form.cleaned_data['dept']
            profile.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('homepage')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('user_login')


@login_required
def profile(request):
    data = Post.objects.filter(authors=request.user)
    # return render(request, "profile.html")
    return render(request, "profile.html", {'data': data})

 

@login_required
def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Updated Successfully')
            update_session_auth_hash(request, form.user)
            return redirect('profile')
    
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'pass_change.html', {'form' : form})



User = get_user_model()

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class OTPVerifyView(View):
    template_name = 'otp_verify.html'
    
    def get(self, request):
        form = OTPForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user_id = request.session.get('otp_user_id')
            if not user_id:
                messages.error(request, 'Session expired or invalid access.')
                return redirect('login')  # Redirect to login if session is not valid

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, 'Invalid user.')
                return redirect('login')
            
            user_otp = UserOTP.objects.filter(user=user, otp=otp).first()
            if user_otp and not user_otp.is_expired():
                login(request, user)
                user_otp.delete()  # OTP can be deleted after successful login
                messages.success(request, 'Logged in successfully')
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid or expired OTP')
        return render(request, self.template_name, {'form': form})
