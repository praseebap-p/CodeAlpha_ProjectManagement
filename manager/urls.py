from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/add-member/', views.add_member, name='add_member'),
    path('project/<int:pk>/create-task/', views.create_task, name='create_task'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('task/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
