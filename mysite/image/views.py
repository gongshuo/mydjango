from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageForm
from .models import Image
from django.http import HttpResponse


@login_required(login_url='/account/login/')
@csrf_exempt
@ require_POST
def upload_image(request):
    # 接收并处理前端提交的数据的函数
    form = ImageForm(data=request.POST)    # 注意：没有传form
    if form.is_valid():
        try:
            new_item = form.save(commit=False)  # 重写，获取图片服务器路径
            new_item.user = request.user
            new_item.save()
            return JsonResponse({'status': "1"})
        except:
            return JsonResponse({'status': "0"})
    else:
        return HttpResponse('输入有误，图片后缀不在jpg, jpeg, png之中‘')


@login_required(login_url='/account/login/')
def list_images(request):
    """图片管理"""
    images = Image.objects.filter(user=request.user)
    return render(request, 'image/list_images.html', {"images": images})


@login_required(login_url='/account/lobin/')
@require_POST
@csrf_exempt
def del_image(request):
    """删除图片"""
    image_id = request.POST['image_id']
    try:
        image = Image.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status': "1"})
    except:
        return JsonResponse({'status': "2"})


def falls_images(request):
    """瀑布图片"""
    images = Image.objects.all()
    return render(request, 'image/falls_images.html', {"images": images})