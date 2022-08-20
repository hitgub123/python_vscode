from django.shortcuts import render


def t1(request):
    return render(request, "t1.html",{'from':__file__})