        项目结构：
            app1模块：
                不使用form和ModelForm的增删改查，上传文件，没做分页组件和数据校验
            app2模块：
                使用form
            app3模块：  

            文计上传没有删除无用文件
            m1-m3模块和t1-t4.py用来测试本地模块的import

        ====================================================================================


        工程目录下，运行django-admin startproject 工程名(djdemo1)，创建django工程。此时工程下会生动djdemo1主模块。
        django-admin startapp(app1) 模块名，创建新的子模块app1。
        python 工程目录/manage.py runserver localhost:8000开启服务器在8000端口

        创建模块后(假设模块名app1)，在/djdemo1\settings.py的INSTALLED_APPS加上'app1',
        django就会在需要时扫描app1里的templates文件夹，查找需要的html文件。
        如果不加的话，需要在TEMPLATES.DIRS里加上app1的templates的路径。比如：
        TEMPLATES = [{'DIRS': [***
                    # os.path.join(BASE_DIR, "/app1/templates/"),
                ],  ***}

        引入静态资源：
        在子模块下创建static/css/a.js,
        在view里返回的html文件顶部加上{% load static %}(否则报错{% load static %}),
        head里加上<script src="{% static 'js/111.js' %}"  ></script>,即可引用该js。
        文件放在其他子模块里也可访问，放在主模块里无法访问。

        django模板遍历数组时可以从{{forloop}}对象获取index，代码如下
            {%for p in products%}
                <div> {{forloop}}>>{{p}}</div>
            {%endfor%}

        request.POST/GET.get('id',1)表示没有id字段时，加上id字段并赋值1.如果有字段但没值，不会给赋值。

        使用ModelForm(对forms.Form无效)时，mpdel.py里如下代码可以在前端显示下拉列表：
            description_choices=(('性价比高','性价比高'),('质量好','质量好'),('销量高','销量高'),('好看','好看'))
            description=models.CharField(choices=description_choices,max_length=11)
                下拉列表显示的是description_choices每个内部元组的第二个值，保存第一个值到数据库。
                这里description字段是char格式，所以把两个值设成一样了。
            description_choices=((1,'性价比高'),(2,'质量好'),(4,'销量高'),(6,'好看'))
            description=models.SmallIntegerField(choices=description_choices,max_length=11)
                如果description是整数，可以这样设置。
                如果是外键，设置 models.ForeignKey即可，不用设置choices

        myform里通过clean钩子函数，对数据进行笔记复杂的验证(比如两次输入的密码是否一样)，检验不通过时可以：
            方法1：推荐，self.add_error可以把error msg写到相应的字段上
            方法2：不推荐，raise ValidationError(error msg)
            要在原页面的对应字段上提示error msg，需要返回原页面，且传form过去。代码如下：
                return render(request, "modelform_update.html", {'form': ProductForm(request.POST)))

        settings.py里可设置报错信息为中文：LANGUAGE_CODE = 'zh-hans'

        ProductForm里设置CharField等，是为了定义检验规则，如果不定义可以不写

        响应ajax请求的views方法需要加上@csrf_exempt注解，否则post请求报错，get可以
        from django.views.decorators.csrf import csrf_exempt

