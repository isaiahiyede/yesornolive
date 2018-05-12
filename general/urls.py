from django.conf.urls import patterns, include, url
from django.conf import settings
import views
from custom_functions import calculator,export_csv

urlpatterns = [
            url(r'^$', views.homepage, name='homepage'),
            url(r'^signup/Page/$', views.register,  name="register"),
            url(r'^login/Page/$', views.user_login,  name="login"),
            url(r'^user-logout/$', views.user_logout,  name="logout"),
            url(r'^events-page/$', views.events_page,  name="events"),
            url(r'^event/(?P<slug>[-\w]+)/(?P<pk>[-\w]+)/$',views.event_details_slug, name="event_details"),
            url(r'^user/dashboard/$',views.user_account, name = "user_account"),
            url(r'^user/profile/$',views.user_profile, name = "profile"),
            url(r'^category/(?P<value>.+)$',views.getCategory, name = "getCategory"),
            url(r'^reality/bbn_coming_soon/$',views.comingSoon, name = "comingSoon"),
            url(r'^categoryLive/(?P<value>.+)$',views.getLiveCategory, name = "getLiveCategory"),
            url(r'^categoryPassed/(?P<value>.+)$',views.getPassedCategory, name = "getPassedCategory"),
            url(r'^about/$',views.about_us, name = "about_us"),
            url(r'^Contact-us/$',views.contact, name = "contact"),
            url(r'^user/messages/$',views.user_messages, name = "messages"),
            url(r'^userComment/$',views.user_comment, name = "user_comment"),
            url(r'^search-results/(?P<action>[-\w]+)/$',views.user_search, name = "user_search"),
            url(r'^ticket/(?P<game_pk>[-\w]+)/$',views.print_ticket, name = "print_ticket"),
            url(r'^user/comments/$',views.view_comment_message, name = "view_comment_message"),
            url(r'^like/comments/(?P<action>[-\w]+)/(?P<pk>.+)/$',views.like_comments, name = "like_comments"),
            url(r'^check/referral/$', views.check_referrer, name="check_referrer"),
            url(r'^calculator/$', calculator, name ="calculator"),
            url(r'^export/csv/$', export_csv, name='export_csv'),
            url(r'^staff-login-access/$', views.staff_login_access, name="staff_login_access"),
            url(r'^faq/$', views.faq, name="faq"),
            url(r'^disclaimer/$', views.disclaimer, name="disclaimer"),
            url(r'^vendor/play/$', views.get_play_event, name="get_play_event"),   
            url(r'^export/tradingDetails/(?P<useracc_obj>[-\w]+)/$', views.tradingDetails, name='tradingDetails'),
            url(r'^closing/djp/$', views.close_djp_client, name="close_djp_client"),
            url(r'^vendor/playDjp/$', views.get_djp_event, name="get_djp_event"),
            url(r'^selected_tickets/$', views.print_selected_tickets, name="print_selected_tickets"),
            url(r'^djp_ticket/(?P<ticket_no>.+)/$',views.print_djp_ticket, name = "print_djp_ticket"),

            url(r'^event/details/(?P<pk>[-\w]+)/$',views.event_details, name="event_details"),
            
]

