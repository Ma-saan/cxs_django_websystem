from django import forms
from .models import Product,Material

class ProductForm(forms.ModelForm):
    # 生産ラインの選択肢を定義
    PRODUCTION_LINE_CHOICES = [
        ('JP1', 'JP1'),
        ('2A', '2A'),
        ('2B', '2B'),
        ('2C', '2C'),
        ('JP3', 'JP3'),
        ('JP4', 'JP4'),
        ('6A', '6A'),
        ('6B', '6B'),
        ('6C', '6C'),
        ('7A', '7A'),
        ('7B', '7B'),
        ('7C', '7C'),
        ('JP8', 'JP8'),
        ('JP9', 'JP9'),
        ('OFF', 'OFF'),
        ('AG', 'AG'),
        ('NS', 'NS'),
    ]
    
    # production_lineフィールドを選択式に上書き
    production_line = forms.ChoiceField(
        choices=PRODUCTION_LINE_CHOICES,
        label='生産ライン',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'production_line']
        labels = {
            'product_id': '製品品番',
            'product_name': '製品名',
        }
        widgets = {
            'product_id': forms.TextInput(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MaterialForm(forms.ModelForm):
    # 単位の選択肢を定義 - MaterialsQC.csvから抽出した実際の値
    UNIT_CHOICES = [
        ('CS', 'CS（ケース）'),
        ('EA', 'EA（個）'),
        ('GM', 'GM（グラム）'),
        ('KG', 'KG（キログラム）'),
        ('LT', 'LT（リットル）')
    ]
    
    # unitフィールドを選択式に上書き
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label='単位',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Material
        fields = ['material_id', 'material_name', 'unit']
        labels = {
            'material_id': '材料品番',
            'material_name': '材料名',
        }
        widgets = {
            'material_id': forms.TextInput(attrs={'class': 'form-control'}),
            'material_name': forms.TextInput(attrs={'class': 'form-control'}),
        }