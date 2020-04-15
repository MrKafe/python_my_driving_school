from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


ROLES = [
    ('student', 'Student'),
    ('instructor', 'Instructor'),
    ('secretary', 'Secretary'),
    ('admin', 'Administrator'),
]


class CreateForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    email = forms.CharField(label="Email", max_length=80)
    driving = forms.CharField(label="Driving license type", max_length=30, required=False)
    role = forms.ChoiceField(
        label='Role',
        widget=forms.RadioSelect,
        choices=ROLES,
        initial='student',
    )
