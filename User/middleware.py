from django.shortcuts import redirect, reverse


def auth_required_middleware(get_response):
    def process_request(request):
        if (not request.user.is_authenticated and
                not request.path.startswith(reverse('login'))):
            print("\033[1;91mAUTHENTICATION REQUESTED FOR ["+request.path+"]\033[m")
            return redirect('login')
        return get_response(request)

    return process_request
