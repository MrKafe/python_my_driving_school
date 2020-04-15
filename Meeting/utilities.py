from django.template.defaultfilters import register
from datetime import datetime


def get_datetime_from_date_hour_minute(date, hour, minute):
    datetime_str = str(date.day).zfill(2) + '/' + str(date.month).zfill(2) + '/' + str(date.year) + ' ' + str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':00'

    return datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
