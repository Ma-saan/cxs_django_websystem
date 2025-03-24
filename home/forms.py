from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=50)

