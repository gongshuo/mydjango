from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import  authenticate, login
from .forms import LoginForm, RegistrationForm, UserForm, UserInfoForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, UserInfo
from django.urls import  reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin

# Create your views here.


def user_login(request):
    """用户登录"""
    if request.method == "POST":
        login_form = LoginForm(request.POST)  # 得到一个赋值后的表单
        if login_form.is_valid():  # 判断表单输入是否正确
            cd = login_form.cleaned_data  # 获取表单数据
            user = authenticate(username=cd['username'], password=cd['password'])  # 内置方法验证表单正确性
            if user:
                login(request, user)
                # 以User实例对象作为参数，实现用户登录。
                # 用户登录之后，Django会自动调用默认的session应用，将用户ID 保存在session中，完成用户登录操作
                return HttpResponse("Wellcome You.You have been authenticated successfully")
            else:
                return HttpResponse("Sorry. Your username or password is not right.")
        else:
            # 返回错误信息
            return HttpResponse("Invalid login,errors:{}".format(login_form.error_messages))

    if request.method == "GET":
        login_form = LoginForm()
        return render(request, "account/login.html", {"form": login_form})


def register(request):
    """用户注册,html由多个Form组成"""
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)  # 赋值后的注册表单
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid()*profile_form.is_valid():
            # user_form.save()  # 执行这句话，密码为空
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])  # 内置的设置密码函数
            # new_user.password = user_form.cleaned_data['password']  # 密码无加密
            new_user.save()

            # profile_form.save()  # 会报错，user为必填项
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            # return HttpResponse("successfully")
            return HttpResponseRedirect(reverse("account:user_login"))
        else:
            return HttpResponse("sorry, your can not register.{}".format(user_form.error_messages))
    else:
        user_form = RegistrationForm()
        profile_form = UserProfileForm()
        return render(request, "account/register.html", {"form": user_form, 'profile': profile_form})


@login_required()
def myself(request):
    """查看我的information"""
    # hasattr() 函数用于判断对象是否包含对应的属性。
    # print(request.user)  # 返回的是用户名，比如root
    if UserProfile.objects.filter(user=request.user).count() != 0:
        userprofile = UserProfile.objects.get(user=request.user)
    else:
        userprofile = UserProfile.objects.create(user=request.user)
    # 和下面等效
    # userprofile = UserProfile.objects.get(user=request.user) if hasattr(request.user, 'userprofile') else UserProfile.objects.create(user=request.user)

    userinfo = UserInfo.objects.get(user=request.user) if hasattr(request.user, 'userinfo') else UserInfo.objects.create(user=request.user)
    return render(request, "account/myself.html", {"user": request.user, "userinfo": userinfo, "userprofile":userprofile})


@login_required(login_url='/account/login/')
def myself_edit(request):
    """编辑我的information"""
    # 两个表其他项都可以为空
    userprofile = UserProfile.objects.get(user=request.user) if hasattr(request.user, 'userprofile') else UserProfile.objects.create(user=request.user)
    userinfo = UserInfo.objects.get(user=request.user) if hasattr(request.user, 'userinfo') else UserInfo.objects.create(user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        userinfo_form = UserInfoForm(request.POST)

        if user_form.is_valid() * userprofile_form.is_valid() * userinfo_form.is_valid():
            user_cd = user_form.cleaned_data
            userprofile_cd = userprofile_form.cleaned_data
            userinfo_cd = userinfo_form.cleaned_data

            request.user.email = user_cd['email']

            userprofile.birth = userprofile_cd['birth']
            userprofile.phone = userprofile_cd['phone']

            userinfo.school = userinfo_cd['school']
            userinfo.company = userinfo_cd['company']
            userinfo.profession = userinfo_cd['profession']
            userinfo.address = userinfo_cd['address']
            userinfo.aboutme = userinfo_cd['aboutme']
            request.user.save()
            userprofile.save()
            userinfo.save()
        return HttpResponseRedirect('/account/my-information/')
    else:
        user_form = UserForm(instance=request.user)  # 实例赋值
        # 初始化
        userprofile_form = UserProfileForm(initial={"birth": userprofile.birth, "phone": userprofile.phone})
        userinfo_form = UserInfoForm(initial={"school": userinfo.school, "company": userinfo.company, "profession":userinfo.profession, "address":userinfo.address, "aboutme":userinfo.aboutme})

        return render(request, "account/myself_edit.html", {"user_form":user_form, "userprofile_form":userprofile_form, "userinfo_form":userinfo_form})


@login_required(login_url='/account/login/')
@xframe_options_sameorigin   # 设置xframe的值
def my_image(request):
    if request.method == 'POST':
        img = request.POST['img']
        userinfo = UserInfo.objects.get(user=request.user.id)
        userinfo.photo = img
        userinfo.save()
        return HttpResponse("1")
    else:
        return render(request, 'account/imagecrop.html',)



