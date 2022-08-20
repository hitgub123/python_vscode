# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Product(models.Model):
    # id = models.AutoField()
    name = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    pic = models.TextField(blank=True, null=True)
    sellpoint = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class Users(models.Model):
    name = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

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
        db_table = 'users'
