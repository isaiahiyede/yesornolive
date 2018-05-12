from django.conf.urls import patterns, include, url
from django.conf import settings
import views


urlpatterns = [

            # url(r'^admin/home/$', views.admin_home, name='adminHome'),
            url(r'^admin/all/(?P<page_to>.+)/$', views.admin_pages, name='admin_pages'),
            url(r'^admin/create-event/$', views.create_new_event, name='create_new_event'),
            url(r'^admin/delete-event/(?P<event_id>[\w]+)/$', views.delete_event, name='delete_event'),
            url(r'^admin/delete-user/(?P<user_id>[\w]+)/$', views.delete_user, name='delete_user'),
            url(r'^admin/edit-event/$', views.view_edit_event, name='view_edit_event'),
            url(r'^admin/edit-user/$', views.edit_user, name='edit_user'),
            url(r'^admin/payment/(?P<status>.+)/$', views.payment_filter, name='payment_filter'),
            url(r'^admin/message/center/$', views.admin_messages, name='admin_messages'),
            url(r'^admin/delete/(?P<pk>[\w]+)/$', views.delete_message, name='delete_message'),
            url(r'^admin/archive/(?P<pk>[\w]+)/$', views.archive_message, name='archive_message'),
            url(r'^admin/event/close/(?P<event_id>[\w]+)/$', views.close_event, name='close_event'),
            url(r'^admin/deleteApprove/comment/(?P<action>.+)/(?P<pk>[\w]+)/$', views.delete_approve_comment, name='delete_approve_comment'),
            url(r'^admin/event/decision/$', views.event_decision, name='event_decision'),
            url(r'^admin/event/validate/$', views.validate_event, name='validate_event'),
            url(r'^admin/stop-event/(?P<pk>[\w]+)/$', views.ban_event, name='ban_event'),
            url(r'^admin/event/players/$', views.get_event_players, name='event_players'),
            url(r'^admin/trader/activity/$', views.get_user_activity, name='get_user_activity'),
            url(r'^admin/cummulative_winnings/$', views.cummulative_winnings, name='cummulative_winnings'),
            url(r'^admin/wjp_amount/$', views.wjp_amount, name="wjp_amount"),
            url(r'^admin/start/wjp/$', views.start_wjp, name="start_wjp"),
            url(r'^admin/close/wjp/(?P<pk>[\w]+)/$', views.close_wjp, name="close_wjp"),
            url(r'^admin/create/djp/$', views.create_djp, name="create_djp"),
            url(r'^admin/update/djp/$', views.edit_djp, name="edit_djp"),
            url(r'^admin/view/djp/$', views.view_djp, name="view_djp"),
            url(r'^admin/dailyreports/$', views.dailyreports, name="dailyreports"),
            url(r'^admin/genericSearch/$', views.genericSearch, name="genericSearch"),
            url(r'^admin/catGamescount/$', views.daily_cat_games_count, name="daily_cat_games_count"),
            url(r'^admin/close-djp/(?P<pk>[\w]+)/$', views.close_djp, name="close_djp"),
            url(r'^admin/users_count/$', views.users_count, name="users_count"),
            url(r'^admin/data_update/$', views.data_update, name="data_update"),
            url(r'^admin/crte_djp_wner/$', views.crte_djp_wner, name="crte_djp_wner"),
            
    ]

