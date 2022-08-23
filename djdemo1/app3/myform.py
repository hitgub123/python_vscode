from dataclasses import fields
from random import choices
from django import forms
from django.core.exceptions import ValidationError

from app3 import models


class ProductForm(forms.ModelForm):
    name=forms.CharField(max_length=11,min_length=2)
    count=forms.IntegerField(max_value=11,min_value=2)
    class Meta:
        model = models.Product
        fields=['name','count','category','pic','time','description']
        # fields = "__all__"
        labels = {
            "name": "商品名称",
            "category": "类别",
            "pic": "画像",
            'time':'最近更新时间'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name,field in self.fields.items():
            if name== 'count':
                continue
            field.widget.attrs={'class': 'form-control','placeholder':field.label}

    
    
    # 钩子，对name字段专用
    def clean_name(self):
        name = self.cleaned_data.get('name')
        # print('clean_name', len(name), self.cleaned_data)
        if name and len(name) != 3:
            # 数据没问题，那么原封不动返回即可
            return name
        else:
            # 错误信息储存到 errors {'__all__':[e,]}
            # raise ValidationError('违法的name')
            self.add_error('name', "name长度不能为3位")

    def clean(self):
        description = self.cleaned_data.get('description')
        # print('clean', len(description), self.cleaned_data)
        if description and len(description) != 3:
            # 数据没问题，那么原封不动返回即可
            return self.cleaned_data
        else:
            # 错误信息储存到 errors {'__all__':[e,]}
            # raise ValidationError('违法的description')
            self.add_error('description', "违法的description")
        