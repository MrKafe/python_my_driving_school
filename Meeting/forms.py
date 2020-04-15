from django import forms
from django.forms import SelectDateWidget
from django.contrib.auth.models import User, Group

select_h = [(i, i) for i in range(8, 21)]
select_m = [(i, i) for i in range(0, 59, 15)]


class CreateForm(forms.Form):
    # student = forms.ChoiceField(label="Student", widget=forms.Select)
    s_group = Group.objects.get(name='student')
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(groups=s_group).filter(profile__hours__gt=0).order_by('username'),
        label="Student",
        widget=forms.Select,
    )
    date = forms.DateField(widget=SelectDateWidget)
    start_at_h = forms.ChoiceField(label="Hour", widget=forms.Select, choices=select_h)
    start_at_m = forms.ChoiceField(label="Minutes", widget=forms.Select, choices=select_m)
    end_at_h = forms.ChoiceField(label="Hour", widget=forms.Select, choices=select_h)
    end_at_m = forms.ChoiceField(label="Minutes", widget=forms.Select, choices=select_m)
