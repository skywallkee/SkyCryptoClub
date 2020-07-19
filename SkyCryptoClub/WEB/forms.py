from django import forms

class LoginForm(forms.Form):

    def clean_username(self):
        cleaned_data = self.clean()
        username = cleaned_data.get('username')
        return username

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))