from django.db import models
from django.core.validators import MaxValueValidator

class Category(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(blank=True, null=True, max_length=10)

    # 返回name，不然下拉列表里会显示Category对象
    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'category'

class Product(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(blank=True, null=True, max_length=10)
    price = models.IntegerField(blank=True, null=True)
    # 最大值为9，后台校验
    count = models.IntegerField(blank=True, null=True, validators=[MaxValueValidator(9)])

    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    pic = models.FileField(upload_to='media',blank=True, null=True)

    sellpoint = models.CharField(blank=True, null=True, max_length=10)

    description_choices=(('性价比高','性价比高'),('质量好','质量好'),('销量高','销量高'),('好看','好看'))
    description=models.CharField(choices=description_choices,max_length=11)

    time = models.DateTimeField(blank=True, null=True)

    # 随便重写一下tostring方法
    def __str__(self) -> str:
        data=self.__dict__
        if(len(data.keys())>100):
            return super().__str__()
        s='{ '
        for k,v in data.items():
            if k.startswith('_'):continue
            s=s+str(k)+" : "+str(v)+' , '
        s=s+' }'
        return s

    class Meta:
        managed = False
        db_table = 'product'
