from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/add_insta_account/', views.addInstaAccount, name='add_insta_account'),
    path("api/start_journey/", views.start_journey, name="start_journey"),
    path('api/get_followers/', views.get_followers, name='get_followers'),
    path('api/get_comments/', views.get_comments, name='get_comments'),
    path('api/ban_offenders/', views.ban_offenders, name='ban_offenders'),
    path('api/delete_process/', views.delete_process, name='delete_process'),
    path('api/continuos_log_poll/', views.continuos_log_poll, name='continuos_log_poll'),
    path('api/save_insta_security_code/', views.save_insta_security_code, name='save_insta_security_code'),
    path('view/account_details/<int:account_id>/', views.account_details_page, name='account_details_page'),
    path('delete/account/<int:account_id>/', views.deleteInstaAcct, name='delete_account'),
    path('system/force_clear_bot/', views.force_clear_bot, name='force_clear_bot'),
]
