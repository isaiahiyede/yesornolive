from django.conf.urls import patterns, include, url
import views


urlpatterns = [
        url(r'login/$', views.login),
        # url(r'find_user_obj/$', views.find_user_obj),
        url(r'validate-event/$', views.validate_decide_event),
        url(r'getEvents/$', views.getEvents),
        url(r'getEventsDecided/$', views.getEventsDecided),
        # url(r'packages/synchronization/$', views.appDBSynchroization),          
]
 