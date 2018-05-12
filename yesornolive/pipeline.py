from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

def save_profile(backend, user, response, *args, **kwargs):
    # UserProfile.objects.create(
    #     user=user, website=response['user']['website'],
    #     instagram_username=response['user']['username'])
    # print "response",response, user, backend
    # if backend.name == 'google-plus':
    #     social_user = UserSocialAuth.objects.get(user=user)
    #     print "uid",social_user.uid
    #     if social_user.uid !="":
    #         pass
    #     else:
    #         social_user.uid = response['id']
    #         social_user.save()    
    return response