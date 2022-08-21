from django.db import models
from django import forms


class Category(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(blank=True, null=True, max_length=10)

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'category'

class Product(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(blank=True, null=True, max_length=10)
    price = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)

    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)

    # pic = models.CharField(blank=True, null=True, max_length=10)
    pic = models.FileField(upload_to='media',blank=True, null=True)

    sellpoint = models.CharField(blank=True, null=True, max_length=10)
    description = models.CharField(blank=True, null=True, max_length=10)
    time = models.DateTimeField(blank=True, null=True)

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
