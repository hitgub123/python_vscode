
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,render

NO_LOGIN_URLS=["/login"]

class MyMiddleware(MiddlewareMixin):
    def process_request(self,request):
        # print('process_request',request.path)
        # print(request.session.__dict__)
        # print(request.session.keys())
        # print(request.session.items())

        #  如果session里有user字段，就不拦截(return)，否则return redirect
        if 'user' in request.session:

        #  如果session里有user字段，且值不为空
        # if request.session.get('user'):
            return
        elif request.path not in NO_LOGIN_URLS:  # 请求的不是登录界面
            request.session['redirect_url']=request.path
            # 以下三种方法都可以拦截原来的请求
            return redirect("/login")
            # return render(request,"login.html")
            # return HttpResponse("请先登录")
 
    def process_response(self,request,response):
        # print("process_response")
        return response   # 必须返回相应对象
