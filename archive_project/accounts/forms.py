from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile
from .constants import DESIGNATION,DEPARTMENT

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'required'}))
    email = forms.EmailField(label='Email Address', widget=forms.EmailInput(attrs={'id': 'required'}))
    contact_number = forms.CharField(label='Contact Number')
    address = forms.CharField(label='Address')
    designation = forms.ChoiceField(choices=DESIGNATION)
    dept = forms.ChoiceField(choices=DEPARTMENT,label='Department')
    image = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'designation', 'dept', 'image']
    def save(self, commit=True):
        our_user=super().save(commit=False)
        if commit:
            our_user.save()
            designation=self.cleaned_data.get('designation')
            dept=self.cleaned_data.get('dept')
            contact_number=self.cleaned_data.get('contact_number')
            address=self.cleaned_data.get('address')
            image=self.cleaned_data.get('image')
            Profile.objects.create(
                user=our_user, 
                designation=designation,
                dept=dept,
                image=image,
                address=address,
                contact_number=contact_number
            )
            
        return our_user

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = ''
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'shadow appearance-none border border-gray-500 rounded w-full py-2 px-3 mb-2 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
            })
            
        

class ChangeUserForm(UserChangeForm):
    designation = forms.ChoiceField(choices=DESIGNATION, widget=forms.Select(attrs={'id': 'required'}))
    dept = forms.ChoiceField(choices=DEPARTMENT,label='Department', widget=forms.Select(attrs={'id': 'required'}))
    contact_number = forms.CharField(label='Contact Number')
    address = forms.CharField(label='Address')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'designation', 'dept']

    def __init__(self, *args, **kwargs):
        super(ChangeUserForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = ''

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'shadow appearance-none border border-gray-500 rounded w-full py-2 px-3 mb-2 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
            })
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_profile, created = Profile.objects.get_or_create(user=user) 

            user_profile.designation = self.cleaned_data['designation']
            user_profile.dept = self.cleaned_data['dept']
            user_profile.address = self.cleaned_data['address']
            user_profile.contact_number = self.cleaned_data['contact_number']
            user_profile.save()
        return user