from django import forms
from django.contrib.auth.models import User
from .models import UserInfo, UserProfile
# from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(min_length=4)
    password = forms.CharField(widget=forms.PasswordInput)
    # hobby = forms.MultipleChoiceField(choices=((1,'篮球'),(2,'足球'),(3,'双色球')))
    error_messages = {
            'required': '用户名是必填项',
            'min_length': '用户名长度不能小于6位'
        }   # form组件默认错误提示都是英文，可以通过这种方式自定义成中文。


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password",  widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Pssword", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")
        # fields = '__all__'  # 生成表中的哪些字段，'__all__'是生成所有的

    def clean_password2(self):
        # 检查的动作在我们调用表单实例对象的is_valid()方法时会被执行。最后执行clean()
        # 以“clean_+属性名称”命名方式所创建的方法，都有类似的功能。
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("passwords do not match.")  # 抛出验证异常
        return cd['password2']

    error_messages = {
            'same': '密码需一致',
        }


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
        fields = ("email", )