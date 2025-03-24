from django import forms

class ScheduleForm(forms.Form):
    selected_rows = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)