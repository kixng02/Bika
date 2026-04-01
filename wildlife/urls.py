from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from wildlife.views import GetNationalParksView
from wildlife.views import GetBorderView
from wildlife.views import GetCityNearParkView
from wildlife.views import DashboardView
from django.contrib.auth import views as auth_views

app_name = "wildlife"
urlpatterns = [
   
    path("home", views.home_view, name="home"),
    path("dashboard", DashboardView.as_view(), name="dashboard"),
 
   
    path("", views.login_view, name="login"),
    path("index", views.login_view, name="index"),

    path("user_signup/", views.user_signup, name="user_signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"), 
    path("update_profile/", views.update_profile, name="update_profile"),

    path("admin_announcements", views.admin_announcements, name="admin_announcements"),
    path("admin_edit_announcement/<int:ann_id>/", views.admin_edit_announcement, name="admin_edit_announcement"),
    path("admin_delete_announcement/<int:ann_id>/", views.admin_delete_announcement, name="admin_delete_announcement"),
    path("admin_create_claim/", views.admin_create_claim, name="admin_create_claim"),
    path("admin_edit_claim/<int:claim_id>/", views.admin_edit_claim, name="admin_edit_claim"),
    path("admin_delete_claim/<int:claim_id>/", views.admin_delete_claim, name="admin_delete_claim"),
    path("admin_support", views.admin_support, name="admin_support"),
    path('admin_support_detail/<int:claim_id>/', views.admin_support_detail, name='admin_support_detail'),
    path('ticket_set_status/<int:ticket_id>/<str:status>/', views.ticket_set_status, name='ticket_set_status'),

    #new templates
    path("admin_claims_list/", views.admin_claims_list, name="admin_claims_list"),
    path("admin_claim_view", views.admin_claim_view, name="admin_claim_view"),
    path("client_claims_list", views.client_claims_list, name="client_claims_list"),
    path("client_new_claim", views.client_new_claim, name="client_new_claim"),
    path("client_announcements_list", views.client_announcements_list, name="client_announcements_list"),
    path("client_announcement_view", views.client_announcement_view, name="client_announcement_view"),

    path('client_support_detail/<int:claim_id>/', views.client_support_detail, name='client_support_detail'),


    path("support/", views.client_support, name="client_support"), 

    #APIS
     path('get_national_parks/', GetNationalParksView.as_view(), name='get_national_parks'),
     path('get_places/', GetCityNearParkView.as_view(), name='get_places'),
     path('get_border/', GetBorderView.as_view(), name='get_border'),

    #ID templates
    path('admin_claim_detail/<int:claim_id>/', views.admin_claim_detail, name='admin_claim_detail'),
    path('approve_claim/<int:claim_id>/', views.approve_claim, name='approve_claim'),
    path('decline_claim/<int:claim_id>/', views.decline_claim, name='decline_claim'),
    path('approved_claims_page/', views.approved_claims_page, name='approved_claims_page'),
    path('declined_claims_page/', views.declined_claims_page, name='declined_claims_page'),
    path('pending_claims_page/', views.pending_claims_page, name='pending_claims_page'),
    path('client_claim_detail/<int:claim_id>/', views.client_claim_detail, name='client_claim_detail'),

    path('information/', views.information_view, name='information'),
    
    # reset password urls
    path('password_reset/',auth_views.PasswordResetView.as_view(success_url='/password_reset/done/'), name= 'password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)