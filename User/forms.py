from django import forms
from .utilities import ROLE_HIERARCHY


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


ROLES = {
    'student': 'Student',
    'instructor': 'Instructor',
    'secretary': 'Secretary',
    'admin': 'Administrator',
}


def get_roles(user):
    role_choice = []

    if user.is_staff:
        for role in ROLES:
            role_choice.append((role, ROLES[role]))
        return role_choice

    user_roles = user.groups.all()
    for role in user_roles:
        for can_create in ROLE_HIERARCHY[role.name]:
            role_choice.append((can_create, ROLES[can_create]))
    # Usage of multiple tuples
    return role_choice


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['role'].choices = get_roles(self.request.user)
        # print(role_choice)

    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    email = forms.CharField(label="Email", max_length=80)
    driving = forms.CharField(label="Driving license type", max_length=30, required=False)
    role = forms.ChoiceField(
        label='Role',
        widget=forms.RadioSelect,
        # choices=ROLES,
        initial='student',
    )
