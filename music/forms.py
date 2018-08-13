from django import forms


class UserForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(widget=forms.EmailInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
