from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username'}),
        }



class UploadQuizForm(forms.Form):
    file = forms.FileField(
        label="Select Excel File",
        help_text="Upload a .xlsx file with your quiz questions"
    )







class RequestOTPForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            "placeholder": "email@example.com",
            "class": "border rounded px-2 py-1 w-full"
        })
    )


class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=8,
        label='OTP',
        widget=forms.TextInput(attrs={
            "placeholder": "Enter OTP",
            "class": "border rounded px-2 py-1 w-full"
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "border rounded px-2 py-1 w-full"}),
        label='New password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "border rounded px-2 py-1 w-full"}),
        label='Confirm new password'
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data