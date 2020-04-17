from datetime import datetime, timedelta
from time import gmtime, strftime
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from . import forms
from User.utilities import is_granted, has_group, get_highest_role
from Meeting.utilities import get_datetime_from_date_hour_minute as get_date
from Meeting.models import Meeting
from django.contrib.auth.models import User
from User.models import Profile


def index(request, filter=None):
    print('\033[96m> Access to appointment list\033[m')

    if is_granted(request.user, 'secretary'):
        if filter:
            view_name = '_admin_row.html'
            user = get_object_or_404(User, pk=filter)
            if has_group(user, 'student'):
                appointments = Meeting.objects.filter(student=user)
            elif has_group(user, 'instructor'):
                appointments = Meeting.objects.filter(instructor=user)
            else:
                return HttpResponseServerError('Impossible to solve this selection,'\
                   ' stop playing with the URL, damn human')
        else:
            appointments = Meeting.objects.all()
            view_name = '_admin_row.html'
        print('\033[96m - Filters : '+(('On: '+'['+user.username+' ('+get_highest_role(user)+')]') if filter
           else 'Off')+'\033[m')
    elif is_granted(request.user, 'instructor'):
        appointments = Meeting.objects.filter(instructor=request.user)
        view_name = '_instructor_row.html'
    elif has_group(request.user, 'student'):
        appointments = Meeting.objects.filter(student=request.user)
        view_name = '_student_row.html'
    else:
        return HttpResponseServerError('This is unexpected... ><')

    print('\033[96m - View : '+view_name+'\033[m')

    return render(request, 'Meeting/index.html', locals())


def create(request):
    if not is_granted(request.user, 'instructor'):
        print('\033[1;91m< User have to be granted [instructor] to create appointments\033[m')
        raise PermissionDenied

    if has_group(request.user, 'instructor'):
        add_instructor = False
    else:
        add_instructor = True

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
            start_at = timedelta(hours=int(form.cleaned_data['start_at_h']), minutes=int(form.cleaned_data['start_at_m']))
            end_at = timedelta(hours=int(form.cleaned_data['end_at_h']), minutes=int(form.cleaned_data['end_at_m']))
            location = form.cleaned_data['location']

            duration_delta = end_at - start_at
            duration_delta_string = strftime('%H:%M', gmtime(duration_delta.total_seconds()))
            t_remains_delta = timedelta(hours=student.profile.time.hour, minutes=student.profile.time.minute)

            if end_at <= start_at:
                has_error = True
                error = 'The appointment have to end AFTER it begin'
                print('\033[91m✕ Could not create appointment: bad hours value \033[m')
            elif t_remains_delta < duration_delta:
                has_error = True
                error = str(student)+' does not have enough hours: '+str(student.profile.time)+'h remaining'
                print('\033[91m✕ Could not create appointment: not enough student credits \033[m')
            else:
                meeting = Meeting(
                    student=student,
                    instructor=instructor,
                    date=date,
                    start_at=strftime('%H:%M', gmtime(start_at.total_seconds())),
                    end_at=strftime('%H:%M', gmtime(end_at.total_seconds())),
                    hours=strftime('%H:%M', gmtime(duration_delta.total_seconds())),
                    location=location,
                )
                student.profile.time = strftime('%H:%M', gmtime((t_remains_delta - duration_delta).total_seconds()))
                meeting.save()
                student.profile.save()

                print('\033[96m> Created new appointment for student/instructor:\n'
                    '   ['+str(student)+'/'+str(instructor)+'] => '+str(meeting.hours)+ 'h\033[m')

                return redirect('index_meet')
        else:
            has_error = True
            error = 'An error has occurred'
            print('\033[91m✕ Invalid form\033[m')
    else:
        print('\033[96m> Access to create appointment\n - Instructor choice: '+('On' if add_instructor else 'Off')
            +'\033[m')
        form = forms.CreateForm(add_instructor=add_instructor)

    return render(request, 'Meeting/create.html', locals())


def edit(request, meet_id):
    try:
        meet = Meeting.objects.get(pk=meet_id)
    except Meeting.DoesNotExist:
        print('\033[1;91m< Cound not find appointment ['+str(meet_id)+']\033[m')
        raise Http404

    if (is_granted(request.user, 'instructor') and meet.instructor.id is request.user.id) \
            or (is_granted(request.user, 'secretary')):

        if has_group(request.user, 'instructor'):
            add_instructor = False
        else:
            add_instructor = True

        if request.method == "POST":
            print('\033[96m> Trying to edit meeting\033[m')
            form = forms.EditForm(request.POST, add_instructor=add_instructor)
            if form.is_valid():
                date = form.cleaned_data['date']
                start_at = timedelta(hours=int(form.cleaned_data['start_at_h']), minutes=int(form.cleaned_data['start_at_m']))
                end_at = timedelta(hours=int(form.cleaned_data['end_at_h']), minutes=int(form.cleaned_data['end_at_m']))
                location = form.cleaned_data['location']

                duration_delta = end_at - start_at
                duration_delta_string = strftime('%H:%M', gmtime(duration_delta.total_seconds()))

                old_start_at = timedelta(hours=meet.start_at.hour, minutes=meet.start_at.minute)
                old_end_at = timedelta(hours=meet.end_at.hour, minutes=meet.end_at.minute)
                diff = gmtime((old_end_at - old_start_at).total_seconds())
                old_duration_delta = timedelta(hours=diff.tm_hour, minutes=diff.tm_min)
                t_remains_delta = timedelta(hours=meet.student.profile.time.hour, minutes=meet.student.profile.time.minute) + old_duration_delta

                if end_at <= start_at:
                    has_error = True
                    error = 'The appointment have to end AFTER it begin'
                    print('\033[91m✕ Could not edit appointment: bad hours value \033[m')
                elif t_remains_delta < duration_delta:
                    has_error = True
                    error = str(meet.student)+' does not have enough hours: '+meet.student.profile.time.strftime('%H:%M')+\
                        'h remaining'
                    print('\033[91m✕ Could not edit appointment: not enough student credits \033[m')
                else:
                    print('\033[96m> Updating appointment for student/instructor ' + str(meet.student) + '/' +\
                          str(meet.instructor)+'\033[m')
                    meet.date = date
                    meet.start_at = strftime('%H:%M', gmtime(start_at.total_seconds()))
                    meet.end_at = strftime('%H:%M', gmtime(end_at.total_seconds()))
                    meet.hours = strftime('%H:%M', gmtime(duration_delta.total_seconds()))
                    meet.location = location
                    meet.save()

                    meet.student.profile.time = strftime('%H:%M', gmtime((t_remains_delta - duration_delta).total_seconds()))
                    meet.student.profile.save()

                    print('\033[96m> Created new appointment for student/instructor:\n'
                        '   ['+str(meet.student)+'/'+str(meet.instructor)+'] => '+str(meet.hours)+'h\033[m')

                    return redirect('index_meet')

        data = {
            'date': meet.date,
            'start_at_h': meet.start_at.strftime("%H"),
            'start_at_m': meet.start_at.strftime("%M"),
            'end_at_h': meet.end_at.strftime("%H"),
            'end_at_m': meet.end_at.strftime("%M"),
            'location': meet.location
        }
        initial = {
            'student': meet.student,
            'instructor': meet.instructor,
        }

        data['start_at_h'] = '{}'.format(data['start_at_h'][1:] if data['start_at_h'].startswith('0') else data['start_at_h'])
        data['start_at_m'] = '{}'.format(data['start_at_m'][1:] if data['start_at_m'].startswith('0') else data['start_at_m'])
        data['end_at_h'] = '{}'.format(data['end_at_h'][1:] if data['end_at_h'].startswith('0') else data['end_at_h'])
        data['end_at_m'] = '{}'.format(data['end_at_m'][1:] if data['end_at_m'].startswith('0') else data['end_at_m'])

        form = forms.EditForm(data=data, initial=initial, add_instructor=add_instructor)

        print('\033[96m> Access to edit appointment\n - Instructor choice: ' + ('On' if add_instructor else 'Off')
              + '\033[m')

        action_param = {'id': meet_id}
        is_edit = True
        return render(request, 'Meeting/create.html', locals())
    else:
        print('\033[1;91m< User have to be\n - granted [instructor] and own appointment\n'\
            ' - granted secretary\033[m')
        raise PermissionDenied


def delete(request, meet_id):
    try:
        meet = Meeting.objects.get(pk=meet_id)
    except Meeting.DoesNotExist:
        print('\033[1;91m< Cound not find appointment [' + str(meet_id) + ']\033[m')
        raise Http404()

    print('\033[96m> Trying to delete meeting\033[m')

    if (is_granted(request.user, 'instructor') and meet.instructor.id is request.user.id) \
            or (is_granted(request.user, 'secretary')):
        start_at = timedelta(hours=meet.start_at.hour, minutes=meet.start_at.minute)
        end_at = timedelta(hours=meet.end_at.hour, minutes=meet.end_at.minute)
        diff = gmtime((end_at - start_at).total_seconds())
        duration_delta = timedelta(hours=diff.tm_hour, minutes=diff.tm_min)
        t_remains_delta = timedelta(hours=meet.student.profile.time.hour, minutes=meet.student.profile.time.minute)
        meet.student.profile.time = strftime('%H:%M', gmtime((t_remains_delta + duration_delta).total_seconds()))
        meet.student.profile.save()
        meet.delete()
    else:
        print('\033[1;91m< User have to be\n - granted [instructor] and own appointment\n'\
            ' - granted secretary\033[m')
        raise PermissionDenied

    return redirect('index_meet')
