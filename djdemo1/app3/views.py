
from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings

from baseApp import utils
from app3 import models
from app3.myform import ProductForm
# 也可以写 from .myform import ProductForm


def home(request):
    return render(request, 'test_extends.html')


def select(request):
    pagesizeS = request.GET.get('pagesize')
    pagesize = int(pagesizeS) if pagesizeS else 7
    pageS = request.GET.get('page')
    page = int(pageS) if pageS else 1
    products = models.Product.objects.order_by(
        '-id')[pagesize*page-pagesize:pagesize*page]
    return render(request, "modelform_list.html", {'objs': products})


def delete(request, id):
    models.Product.objects.get(id=id).delete()
    return redirect("/a3/list")


def addORupdate(request, id):
    if request.method == "GET":
        # id=0表示add，非0表示update
        if (id == 0):
            return render(request, "modelform_update.html", {'form': ProductForm(), 'obj': {'id': id}})
         # 获取单个对象
        obj = models.Product.objects.get(id=id)
        # print(obj.__dict__,type(obj))
        obj = obj.__dict__
        # 外键字段自动加id，和页面匹配不上，手动赋值
        obj['category'] = obj['category_id']
        form = ProductForm(data=obj)
        # form = ProductForm(obj)
        # template页面获取不到pic，手动赋值
        return render(request, "modelform_update.html", {'form': form, 'obj': {'id': id, 'pic': obj['pic']}})

    form_obj = ProductForm(request.POST, request.FILES)
    # print(request.POST)
    # print(request.FILES)

    # 利用form内置方法校验前端得到的数据
    # 报错'ProductForm' object has no attribute 'cleaned_data'，需要调用is_valid方法后才能使用
    # print(form_obj.cleaned_data.get('name','1'))
    if form_obj.is_valid():
        myfile = request.FILES.get('pic', None)

       # 有上传文件就更新db的pic字段
        if myfile:
            try:
                filename = utils.upload_file(myfile, settings.MEDIA_ROOT)
                form_obj.cleaned_data['pic'] = settings.MEDIA_URL+filename
            except Exception as e:
                return HttpResponse(e)

        # print('before',form_obj.cleaned_data)
        form_obj.cleaned_data['category_id'] = request.POST['category']
        form_obj.cleaned_data.pop('category')
        form_obj.cleaned_data['time'] = datetime.now()

        # 如果没有上传，对象的pic是None，db的pic会被更新成None。所以去掉对象的pic属性
        if not myfile:
            form_obj.cleaned_data.pop('pic')

        # print('after', form_obj.cleaned_data)

        if id == 0:
            models.Product(**form_obj.cleaned_data).save()
        else:
            models.Product.objects.filter(
                id=id).update(**form_obj.cleaned_data)
        return redirect("/a3/list")
    else:
        print(form_obj.errors)
        datamap = {'form':  ProductForm(request.POST),  'obj': {'id': id,  'pic': request.POST.get('pic')}}
        return render(request, "modelform_update.html", datamap)
