from datetime import datetime
from django.http import Http404, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from . import forms
from User.utilities import is_granted, has_group
from Meeting.utilities import get_datetime_from_date_hour_minute as get_date
from Meeting.models import Meeting
from User.models import Profile


def index(request, filter=None):
    print('\033[96m> Accessing appointment page\033[m')

    if is_granted(request.user, 'secretary'):
        appointments = Meeting.objects.all()
    elif is_granted(request.user, 'instructor'):
        appointments = Meeting.objects.filter(instructor=request.user)
    elif has_group(request.user, 'student'):
        appointments = Meeting.objects.filter(student=request.user)
    else:
        raise HttpResponseServerError

    view_name = '_admin_row.html' if is_granted(request.user, 'secretary') \
        else '_instructor_row.html' if has_group(request.user, 'instructor') \
        else '_student_row.html'

    print('\033[96m - View : '+view_name+'\033[m')

    return render(request, 'Meeting/index.html', locals())


def create(request):
    if not is_granted(request.user, 'instructor'):
        raise PermissionDenied

    if has_group(request.user, 'instructor'):
        add_instructor = False
    else:
        add_instructor = True

    print('\033[96m> Accessing create appointment page\033[m')

    has_error = False
    if request.method == "POST":
        print('\033[96m> Trying to create meeting\033[m')

        form = forms.CreateForm(request.POST, add_instructor=add_instructor)
        if form.is_valid():
            student = form.cleaned_data['student']
            if add_instructor:
                instructor = form.cleaned_data['instructor']
            else:
                instructor = request.user
            date = form.cleaned_data['date']
            start_at = get_date(date, form.cleaned_data['start_at_h'], form.cleaned_data['start_at_m'])
            end_at = get_date(date, form.cleaned_data['end_at_h'], form.cleaned_data['end_at_m'])
            location = form.cleaned_data['location']

            # TODO: This only take into account HOURS => add MINUTES
            diff = end_at - start_at
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            if end_at <= start_at:
                has_error = True
                error = 'The appointment have to end AFTER it begin'
            elif student.profile.hours < hours:
                has_error = True
                error = str(student)+' does not have enough hours: '+str(student.profile.hours)+'h remaining'
            else:
                print('\033[96m> Creating new appoint for student/instructor '+str(student)+'/'+str(instructor)+' : '+\
                      str(hours)+'h\033[m')
                meeting = Meeting(
                    student=student,
                    instructor=instructor,
                    date=date,
                    start_at=start_at,
                    end_at=end_at,
                    hours=datetime.strptime(str(hours), '%H'),
                    location=location,
                )
                meeting.save()
                return redirect('index_meet')
        else:
            has_error = True
            error = 'An error has occured'
    else:
        print('\033[96m> Accessed create meeting page\033[m')
        form = forms.CreateForm(add_instructor=add_instructor)

    return render(request, 'Meeting/create.html', locals())


def edit(request, meet_id):
    if not is_granted(request.user, 'instructor'):
        raise PermissionDenied

    try:
        meet = Meeting.objects.get(pk=meet_id)
    except Meeting.DoesNotExist:
        raise Http404("No MyModel matches the given query.")

    if has_group(request.user, 'instructor'):
        add_instructor = False
    else:
        add_instructor = True

    if request.method == "POST":
        print('\033[96m> Trying to create meeting\033[m')

        form = forms.CreateForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            if add_instructor:
                instructor = form.cleaned_data['instructor']
            else:
                instructor = request.user
            date = form.cleaned_data['date']
            start_at = get_date(date, form.cleaned_data['start_at_h'], form.cleaned_data['start_at_m'])
            end_at = get_date(date, form.cleaned_data['end_at_h'], form.cleaned_data['end_at_m'])
            location = form.cleaned_data['location']

            # TODO: This only take into account HOURS => add MINUTES
            diff = end_at - start_at
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            if end_at <= start_at:
                has_error = True
                error = 'The appointment have to end AFTER it begin'
            elif student.profile.hours < hours:
                has_error = True
                error = str(student) + ' does not have enough hours: ' + str(student.profile.hours) + 'h remaining'
            else:
                print('\033[96m> Updating appointment for student/instructor ' + str(student) + '/' + str(
                    instructor) + ' : ' + \
                      str(hours) + 'h\033[m')
                meet.student = student
                meet.instructor = instructor
                meet.date = date
                meet.start_at = start_at
                meet.end_at = end_at
                meet.hours = datetime.strptime(str(hours), '%H')
                meet.location = location
                meet.save()
                return redirect('index_meet')

    if (is_granted(request.user, 'instructor') and meet.instructor.id is request.user.id)\
            or (is_granted(request.user, 'secretary')):
        data = {
            'student': meet.student,
            'date': meet.date,
            'start_at_h': meet.start_at.strftime("%H"),
            'start_at_m': meet.start_at.strftime("%M"),
            'end_at_h': meet.end_at.strftime("%H"),
            'end_at_m': meet.end_at.strftime("%M"),
            'location': meet.location
        }

        data['start_at_h'] = '{}'.format(data['start_at_h'][1:] if data['start_at_h'].startswith('0') else data['start_at_h'])
        data['start_at_m'] = '{}'.format(data['start_at_m'][1:] if data['start_at_m'].startswith('0') else data['start_at_m'])
        data['end_at_h'] = '{}'.format(data['end_at_h'][1:] if data['end_at_h'].startswith('0') else data['end_at_h'])
        data['end_at_m'] = '{}'.format(data['end_at_m'][1:] if data['end_at_m'].startswith('0') else data['end_at_m'])
        form = forms.CreateForm(data)

        action_param = {'id': meet_id}
        is_edit = True
        return render(request, 'Meeting/create.html', locals())
    else:
        raise PermissionDenied
