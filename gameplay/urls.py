from django.conf.urls import patterns, include, url
from django.conf import settings
import views


urlpatterns = [

        url(r'^betting/$',views.betting, name = "betting"),
        url(r'^vendor/gameplay/$',views.vendor_game_play, name = "vendor_game_play"),
        url(r'^dailyjackpot/$',views.dailyjackpot2, name = "dailyjackpot2"),
        url(r'^weeklyjackpot/$',views.weeklyjackpot2, name = "weeklyjackpot2"),
        url(r'^user_entries/$',views.user_entries, name = "user_entries"),
        url(r'^vendor/dailyjackpot/$',views.vendor_dailyjackpot, name = "vendor_dailyjackpot"),

        url(r'^dailyjkp/$',views.dailyjackpot, name = "dailyjackpot"),
        url(r'^weeklyjkp/$',views.weeklyjackpot, name = "weeklyjackpot"),
        
]