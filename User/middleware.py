from django.shortcuts import redirect, reverse
from User import utilities as us


def auth_required_middleware(get_response):
    def process_request(request):
        if (not request.user.is_authenticated and
                not request.path.startswith(reverse('login'))):
            print("\033[1;91mAUTHENTICATION REQUESTED FOR ["+request.path+"]\033[m")
            return redirect('login')
        return get_response(request)

    return process_request


def user_icon_middleware(get_response):
    def user_icon(request):
        if request.user.is_authenticated:
            u = request.user
            if u.is_staff:
                u.icon = '<i class="fa fa-black-tie"></i>'
            elif us.is_granted(u, 'admin'):
                u.icon = '<i class="fa fa-user-plus"></i>'
            elif us.is_granted(u, 'secretary'):
                u.icon = '<i class="fa fa-laptop"></i>'
            elif us.is_granted(u, 'instructor'):
                u.icon = '<i class="fa fa-car"></i>'
            else:
                u.icon = '<i class="fa fa-user"></i>'
            print('Icon is: '+u.icon)
            request.user = u
        return get_response(request)

    return user_icon
