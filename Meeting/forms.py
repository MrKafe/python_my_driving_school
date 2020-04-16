from django import forms
from django.forms import SelectDateWidget
from django.contrib.auth.models import User, Group
from django.db.models import Q

select_h = [(i, i) for i in range(8, 21)]
select_m = [(i, i) for i in range(0, 59, 15)]


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.add_instructor = kwargs.pop("add_instructor", None)
        super(CreateForm, self).__init__(*args, **kwargs)
        if not self.add_instructor:
            print("Do not display instructors")
            del self.fields['instructor']

    class Meta:
        fields = ('student', 'instructor', 'date', 'start_at_h', 'start_at_m', 'end_at_h', 'end_at_m', 'location',)

    s_group = Group.objects.get(name='student')
    i_group = Group.objects.get(name='instructor')

    student = forms.ModelChoiceField(
        # use Q to make queries with OR statement
        queryset=User.objects.filter(groups=s_group).filter(Q(profile__time__hour__gt=0) | \
            Q(profile__time__minute__gt=0)).order_by('username'),
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


class EditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.add_instructor = kwargs.pop("add_instructor", None)
        super(EditForm, self).__init__(*args, **kwargs)
        if not self.add_instructor:
            print("Do not display instructors")
            del self.fields['instructor']

    class Meta:
        fields = ('student', 'instructor', 'date', 'start_at_h', 'start_at_m', 'end_at_h', 'end_at_m', 'location',)

    # No need to check if use manually changed value before form submit;
    #    Even if a user tampers with the field’s value submitted to the server,
    #    it will be ignored in favor of the value from the form’s initial data
    # From the Django's man
    student = forms.CharField(widget=forms.TextInput(), label="Student", disabled=True, required=False)
    instructor = forms.CharField(widget=forms.TextInput(), label="Instructor", disabled=True, required=False)
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
