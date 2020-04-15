from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import register


ROLE_HIERARCHY = {
    'student': [],
    'instructor': ['student'],
    'secretary': ['instructor', 'student'],
    'admin': ['secretary', 'instructor', 'student'],
}


def find_existing_user(username):
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    return True


def get_inheritance_roles(user, strict=False, only_id=False):
    user_roles = user.groups.all()
    unique_list = []
    for user_role in user_roles:
        if not strict and user_role not in unique_list:
            role = Group.objects.get(name=user_role).id if only_id else user_role
            unique_list.append(role)
        if user_role.name in ROLE_HIERARCHY.keys():
            inherit = ROLE_HIERARCHY[user_role.name]
            for allowed in inherit:
                allowed = Group.objects.get(name=allowed).id if only_id\
                    else allowed
                if allowed not in unique_list:
                    unique_list.append(allowed)
    return unique_list

@register.filter(name='granted')
def is_granted(user, role, strict=False):
    if user.is_staff:
        # print('\033[92m> Staff is always granted\033[m')
        return True

    # to_print = '\033[96m> Checking if user ' + user.username + ' is granted [' + role + ']'
    # to_print = to_print + ' as Strict inheritance' if strict is True else ''
    # print(to_print + '\033[m')
    user_roles = user.groups.all()
    for user_role in user_roles:
        if not strict and user_role.name == role:
            # print('\033[92m - User ' + user.username + ' have role [' + role + ']\033[m')
            return True
        elif not strict:
            # print('\033[33m - User ' + user.username + ' does not have role [' + role + ']\033[m')
            pass

        if user_role.name in ROLE_HIERARCHY.keys():
            # print('\033[96m - Role [' + role + '] is known in hierarchy: checking inherit roles\033[m')
            inherit = ROLE_HIERARCHY[user_role.name]
            for allowed in inherit:
                if allowed == role:
                    # print('\033[92m   - User ' + user.username + ' have role [' + role + '] by inheritance\033[m')
                    return True
            # print('\033[91m   - User ' + user.username + ' does not have role [' + role + '] by inheritance\033[m')
        else:
            # print('\033[96m - Role [' + role + '] isn\'t in role hierarchy\033[m')
            pass

    return False


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    return group in user.groups.all()


# TODO: Add more validations on User on create/edit
def check_user(form):
    return True
