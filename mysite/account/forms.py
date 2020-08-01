from django import forms
from django.contrib.auth.models import  User
from .models import UserInfo, UserProfile
# from .models import


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Pssword", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password2(self):
        # 检查的动作在我们调用表单实例对象的is_valid()方法时会被执行。
        # 以“clean_+属性名称”命名方式所创建的方法，都有类似的功能。
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("passwords do not match.")
        return cd['password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("phone", "birth")


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ("school", "company", "profession", "address", "aboutme", 'photo')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)