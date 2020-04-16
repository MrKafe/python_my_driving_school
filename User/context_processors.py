from User.models import User


def con_test(request):
    context_data = dict()
    context_data['test'] = 5
    return context_data
