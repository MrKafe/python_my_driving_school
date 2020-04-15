from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied


from . import forms
from User.utilities import is_granted, has_group
from Meeting.utilities import get_datetime_from_date_hour_minute as get_date
from Meeting.models import Meeting
from User.models import Profile


def index(request, filter=None):
    print('\033[96m> Accessing appointment page\033[m')
    if not is_granted(request.user, 'instructor'):
        raise PermissionDenied

    appointments = Meeting.objects.all()

    view_name = '_admin_row.html' if is_granted(request.user, 'secretary') \
        else '_instructor_row.html' if has_group(request.user, 'instructor') \
        else '_student_view'

    print('\033[96m - View : '+view_name+'\033[m')

    return render(request, 'Meeting/index.html', locals())


def create(request):
    if not is_granted(request.user, 'instructor'):
        raise PermissionDenied

    print('\033[96m> Accessing create appointment page\033[m')

    has_error = False
    if request.method == "POST":
        print('\033[96m> Trying to create meeting\033[m')

        form = forms.CreateForm(request.POST)
        if form.is_valid():
            # TODO: Check if student have enough hours
            student = form.cleaned_data['student']
            if has_group(request.user, 'instructor'):
                instructor = request.user
            elif is_granted(request.user, 'secretary'):
                pass
            date = form.cleaned_data['date']
            start_at = get_date(date, form.cleaned_data['start_at_h'], form.cleaned_data['start_at_m'])
            end_at = get_date(date, form.cleaned_data['end_at_h'], form.cleaned_data['end_at_m'])

            if end_at <= start_at:
                has_error = True
                error = 'Your appointment have to end AFTER it begin'
            else:
                meeting = Meeting(student=student, instructor=instructor, date=date, start_at=start_at, end_at=end_at)
                meeting.save()
                return redirect('index_meet')
        else:
            has_error = True
            error = 'An error has occured'
    else:
        print('\033[96m> Accessed create meeting page\033[m')
        form = forms.CreateForm()

    return render(request, 'Meeting/create.html', locals())

