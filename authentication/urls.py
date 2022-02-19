from django.urls import path
from .apiViews import ModelView
from . import views


urlpatterns = [
    path('api/model/', ModelView.as_view()),
    path('pred',views.model_classifier,name="index4"),
    path('signin/', views.signIn),
   	path('postsignIn/', views.postsignIn),
   	path('signup/', views.signUp, name="signup"),
   	path('logout/', views.logout, name="log"),
   	path('postsignUp/', views.postsignUp),
    path('profile/', views.profile),
    path('abt/',views.abt),
    path('reset/', views.reset),
    path('postReset/', views.postReset),
    path('gsignin/', views.googlesignin),
    path('update/', views.authupdate),
    path('delete/', views.authdelete),
    path('changepass/',views.changepass),
]
