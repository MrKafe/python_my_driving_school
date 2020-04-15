from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group


class Meeting(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, db_column='student_id', related_name='student')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, db_column='instructor_id', related_name='instructor')
    date = models.DateField()
    start_at = models.TimeField()
    end_at = models.TimeField()
    hours = models.TimeField()
    location = models.TextField(null=True)
