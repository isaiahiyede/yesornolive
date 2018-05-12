from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailAuthBackEnd(ModelBackend):

    def authenticate(self, email=None, password=None, **kwargs):

        try:
            '''For site and admin login'''
            #if kwargs.has_key('marketer'):
            if kwargs:
                user = User.objects.get(email=email, useraccount__marketer = kwargs.get('marketer'))
                # user = User.objects.get(email=email, subscriber__user__email = email)
            else:
                user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None


class UsernameAuthBackEnd(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            '''For site and admin login'''
            #if kwargs.has_key('marketer'):
            if kwargs:
                user = User.objects.get(username=username, useraccount__marketer = kwargs.get('marketer'))
                # user = User.objects.get(username=username, subscriber__user__username=username)
            else:
                user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

