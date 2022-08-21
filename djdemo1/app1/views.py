from datetime import datetime
from app2 import models
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
from baseApp import utils



def hello(request):
    return HttpResponse("Hello world ! ")

# render , set parameters for response, django template


def t1(request):
    user = {'name': 'John', 'age': 11, 'password': 'aaa'}
    products = [{'product': '苹果{}'.format(
        i), 'price': i*10+1} for i in range(5)]
    return render(request, "t1.html", {'from': __file__, 'user': user, 'products': products})

# set static/css or js for html files


def t2(request):
    print(request.method)
    print(request.GET)
    print(request.POST)
    return render(request, "t2.html")

# {% csrf_token %} , redirect ,request.method/GET/POST


def login(request):
    print(request.method)
    if request.method == "GET":
        print(request.GET)
        return render(request, "login.html")
    if request.method == "POST":
        print(request.POST)
        if request.POST.get('password'):
            pwd = request.POST['password']
            print(type(pwd), pwd)
            return redirect('/a1/t1')
    return render(request, "login.html", {'msg': 'password error'})


def select(request):
    # 通过objects这个模型管理器的all()获得所有数据行，相当于SQL中的SELECT * FROM
    # products = models.Product.objects.all()


    # filter相当于SQL中的WHERE，可设置条件过滤结果
    # products = models.Product.objects.filter(id=21)

    # <=
    # products = models.Product.objects.filter(id__lte=23)
    

    # 限制返回的数据 相当于 SQL 中的 OFFSET 0 LIMIT 5;
    # products=models.Product.objects.order_by('name')[0:5]

    # 数据排序,-id表示id逆序
    # products=models.Product.objects.order_by("id")

    # 上面的方法可以连锁使用，in list
    # products=models.Product.objects.filter(id__in =[21,22,23,666]).order_by("-id")

    # print('filter>>', products)

    pagesizeS = request.GET.get('pagesize')
    pagesize = int(pagesizeS) if pagesizeS else 5
    pageS = request.GET.get('page')
    page=int(pageS) if pageS else 1
    products = models.Product.objects.order_by(
        'id')[pagesize*page-pagesize:pagesize*page]
    return render(request, "list.html", {'objs': products})

def delete(request, id):
    # 删除id=1的数据
    # models.Product.objects.get(id=1).delete()

    # 另外一种方式
    # models.Product.objects.filter(id=1).delete()

    # 删除所有数据
    # models.Product.objects.all().delete()

    #get找不到会报错，filter会返回空`数组`
    models.Product.objects.get(id=id).delete()
    return redirect("/a1/list")


def addORupdate(request, id):
    if request.method == "GET":
        if (id == 0):
            return render(request, "update.html", {'obj': {'id': id}})
         # 获取单个对象
        # obj = models.Product.objects.get(id=id)
        obj = models.Product.objects.filter(id=id).first()
        return render(request, "update.html", {'obj': obj})
    # print(request.GET)
    # print(id)

    myfile = request.FILES.get('pic',None)
    try:
        filename=utils.upload_file(myfile, settings.MEDIA_ROOT)
    except Exception as e:
        return HttpResponse(e)

    objmap={
        'name': request.POST.get('name', 'No Name'),
        'price': request.POST.get('price', 250),
        'count': request.POST.get('count', 7),
        'category_id': request.POST.get('category', 'No category'),
        'pic': settings.MEDIA_URL+filename,
        'description': request.POST.get('description', 'No Description'),
        'time':datetime.now()
    }
    # print(request.FILES)
    print('>>',objmap)
    if  id==0:
        obj=models.Product(**objmap)
        obj.save()
    else:
        models.Product.objects.filter(id=id).update(**objmap)
    return redirect("/a1/list")


def update(request):
    # 修改其中一个id=21的name字段，再save，相当于SQL中的UPDATE
    # obj = models.Product.objects.get(id=21)
    # obj.count += 1
    # obj.save()

    # 另外一种方式
    # models.Product.objects.filter(id=25).update(name='Google')

    # 修改所有的列
    # models.Product.objects.all().update(pic='qq.jpg')

    return HttpResponse("<p>修改成功</p>")
