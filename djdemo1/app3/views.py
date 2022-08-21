from django import forms
from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.exceptions import ValidationError

from baseApp import utils
from app3 import models


class ProductForm(forms.Form):
    # id自增字段，不放入
    # id = forms.CharField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(
        min_length=2,  # 设置最小长度
        max_length=9,  # 设置最大长度
        label="商品名",  # 设置标签名
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    # name = forms.CharField(label="商品名")
    # name.widget = forms.TextInput()

    price = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'}))
    count = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'}))

    category = forms.fields.ChoiceField(
        # choices=((1, "篮球"), (2, "足球"), (3, "双色球"), ),
        widget=forms.widgets.Select(attrs={'class': 'form-control'}), initial=0)

    pic = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control'}), required=False)

    sellpoint = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'}))
    time = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'}), initial=datetime.now())

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        #  数据变成动态的从数据库中获取
        init_choices = (0, 'please select')
        db_choices = list(
            models.Category.objects.all().values_list('id', 'name'))
        db_choices.insert(0, init_choices)
        # print(db_choices)
        self.fields['category'].choices = db_choices

    # 全局钩子
    def clean(self):
        """在通过基础验证的干净数据中get获取字段"""
        description = self.cleaned_data.get('description')
        print('clean', len(description), self.cleaned_data)
        if len(description) != 3:
            # 数据没问题，那么原封不动返回即可
            return self.cleaned_data
        else:
            # 错误信息储存到 errors {'__all__':[e,]}
            raise ValidationError('违法的description')

def home(request):
    return render(request, 'test_extends.html')


def t1(request):
    return render(request, "t1.html", {'from': __file__})


def select(request):
    pagesizeS = request.GET.get('pagesize')
    pagesize = int(pagesizeS) if pagesizeS else 7
    pageS = request.GET.get('page')
    page = int(pageS) if pageS else 1
    products = models.Product.objects.order_by(
        'id')[pagesize*page-pagesize:pagesize*page]
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
        form = ProductForm(obj)
        # template页面获取不到pic，手动赋值
        return render(request, "modelform_update.html", {'form': form, 'obj': {'id': id, 'pic': obj['pic']}})
    # print(request.GET)
    # print(id)

    form_obj = ProductForm(request.POST, request.FILES)
    print(request.POST)
    print(request.FILES)
    # print('register_obj',form_obj.is_valid(),form_obj.errors)

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
        # print(form_obj.cleaned_data.get('name','1'))        #request.POST.get('name')
        # print(form_obj.cleaned_data.get('name1','2'))       #2

        # print('before',form_obj.cleaned_data)
        form_obj.cleaned_data['category_id'] = form_obj.cleaned_data['category']
        form_obj.cleaned_data.pop('category')
        form_obj.cleaned_data['time'] = datetime.now()

        # 如果没有上传，对象的pic是None，db的pic会被更新成None。所以去掉对象的pic属性
        if not myfile:
            form_obj.cleaned_data.pop('pic')

        print('after', form_obj.cleaned_data)

        if id == 0:
            models.Product(**form_obj.cleaned_data).save()
        else:
            models.Product.objects.filter(
                id=id).update(**form_obj.cleaned_data)
        return redirect("/3/list")
    else:
        print(form_obj.errors)
        form = ProductForm(request.POST)
        # print('error',form_obj.cleaned_data)
        datamap = {'form': form, 'pic':request.POST.get('pic'),'obj': {'id': id, 'msg': form_obj.errors}}
        return render(request, "modelform_update.html", datamap)
