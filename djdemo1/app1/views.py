from django.shortcuts import render, redirect
from django.http import HttpResponse
from app2 import models


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


def list(request):
    users=models.Users.objects.all()
    print(users)
    
    return render(request, "list.html", {})
