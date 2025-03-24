from django import forms


class EventForm(forms.Form):

    rooms = [
        ('1','会議室1'),
        ('2','会議室2'),
        ('3','会議室3'),
        ('4','応接室')
    ]

    start_date = forms.IntegerField(required=True)
    end_date = forms.IntegerField(required=True)
    event_name = forms.CharField(required=True, max_length=10)
    person = forms.CharField(required=True, max_length=10)
    """
    room_name = forms.ModelChoiceField(
        required=True,
          disabled=False,
          initial=['1'],
          choices=rooms,
          widget=forms.Select(attrs={
               'id': 'one',}))
    """
    room_name = forms.CharField(required=True, max_length=6)

class CalendarForm(forms.Form):

    start_date = forms.IntegerField(required=True)
    end_date = forms.IntegerField(required=True)
    
