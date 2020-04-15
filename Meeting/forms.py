from django import forms
from django.forms import SelectDateWidget
from django.contrib.auth.models import User, Group

select_h = [(i, i) for i in range(8, 21)]
select_m = [(i, i) for i in range(0, 59, 15)]


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.add_instructor = kwargs.pop("add_instructor", None)
        super(CreateForm, self).__init__(*args, **kwargs)
        if not self.add_instructor:
            del self.fields['instructor']

    class Meta:
        fields = ('student', 'instructor', 'date', 'start_at_h', 'start_at_m', 'end_at_h', 'end_at_m', 'location',)

    s_group = Group.objects.get(name='student')
    i_group = Group.objects.get(name='instructor')

    student = forms.ModelChoiceField(
        queryset=User.objects.filter(groups=s_group).filter(profile__hours__gt=0).order_by('username'),
        label="Student",
        widget=forms.Select,
    )
    instructor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups=i_group).order_by('username'),
        label="Instructor",
        widget=forms.Select,
    )
    date = forms.DateField(widget=SelectDateWidget)
    start_at_h = forms.ChoiceField(label="Hour", widget=forms.Select, choices=select_h)
    start_at_m = forms.ChoiceField(label="Minutes", widget=forms.Select, choices=select_m)
    end_at_h = forms.ChoiceField(label="Hour", widget=forms.Select, choices=select_h)
    end_at_m = forms.ChoiceField(label="Minutes", widget=forms.Select, choices=select_m)
    location = forms.CharField(
        widget=forms.TextInput(),
        label='Address',
        required=False
    )
