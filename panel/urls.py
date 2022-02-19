from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/', views.dashboard),
    path('user/',views.user_table),
    path('user/search/email',views.searchquser),
    path('user/<str:x>', views.query),

    path('logout/',views.logoutview),
    path('user/disable/<str:x>',views.disable),
    path('user/enable/<str:x>', views.enable),
    path('user/delete/<str:x>', views.delete_user),
    path('user/update/<str:x>', views.update_user),
    path('user/delete/<str:x>/<str:y>/<str:z>',views.delete_query),
    path('admintb/',views.admin_table),
    path('cradmin1/',views.create_admin1),
    path('cradmin2/', views.create_admin2),
    path('cradmin3/', views.create_admin3),
    path('cradmin4/', views.create_admin4),

]

