# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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

    # 用哪个都行，手动保存文件和pic的路径
    pic = models.CharField(blank=True, null=True, max_length=10)
    # pic = models.FileField(upload_to='media',blank=True, null=True)

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
