from django.urls import path, include
from . import views
from . import models



urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    # path("products/<slug:t_name>/$", views.productView, name="ProductView"),
    path("ty/", views.ty, name="ty"),
    

    path("checkout/", views.checkout, name="Checkout"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("edit_profile/", views.edit_profile, name='edit_profile'),
    path('change_password', views.change_password, name="change_password"),
]