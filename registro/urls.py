from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('registro-publico/', views.registro_publico, name='registro_publico'),


    # Pasamos el ID del registro en la URL (ejemplo /credencial/1/)
    path('credencial/<int:registro_id>/', views.credencial, name='credencial'),
    # Nuevas rutas para el Check-in
    path('checkin/', views.checkin_buscador, name='checkin_buscador'),
    path('checkin/marcar/<int:registro_id>/', views.hacer_checkin, name='hacer_checkin'),

    # Nuevas rutas para Control de Sala
    path('sala/', views.control_sala, name='control_sala'),
    path('sala/registrar/', views.registrar_asistencia, name='registrar_asistencia'),

    # Nuevas rutas para Reportes
    path('reportes/', views.reportes_dashboard, name='reportes'),
    path('reportes/exportar/csv/', views.exportar_asistencias_csv, name='exportar_csv'),

    # Rutas de Autenticación (Login / Logout)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
]