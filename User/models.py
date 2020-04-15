from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    driving_license = models.CharField(max_length=42, null=True, blank=True)
    hours = models.IntegerField(default=0, null=True)
    time = models.TimeField(null=True)


    def __str__(self):
        return self.user.username

# from django.contrib.auth.models import User
# from User.models import Profile
# user = User.objects.create_user('', 'mail+@gmail.com', 'qwerty')
# profile = Profile(user=user, driving_license='A2')
# profile.save()
#