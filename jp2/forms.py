from django import forms
from .models import Jp2

class Jp2Form(forms.ModelForm):
    class Meta:
        model = Jp2
        fields = ['item_no', 'item_name', 'warning']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_no'].widget.attrs['placeholder'] = '品番を選択してください'
        self.fields['item_name'].widget.attrs['placeholder'] = '製品名を選択してください'
