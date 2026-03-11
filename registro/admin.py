from django.contrib import admin
from .models import (
    Congress, Participant, Registration, QRCode, 
    Session, Attendance, BadgePrintLog, AuditLog, Speaker, ForumSpeaker
)

@admin.register(Congress)
class CongressAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location')
    search_fields = ('name', 'location')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    # Mostramos columnas clave en la lista
    list_display = ('name', 'document_id', 'email', 'is_utp', 'utp_career')
    # Barra de búsqueda por nombre, cédula o correo
    search_fields = ('name', 'document_id', 'email')
    # Filtros laterales para ver rápidamente a los de la UTP
    list_filter = ('is_utp', 'utp_career')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('participant', 'congress', 'status', 'registered_at')
    list_filter = ('status', 'congress')
    search_fields = ('participant__name', 'participant__document_id')

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('registration', 'token', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('token', 'registration__participant__name')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'congress', 'room', 'start_time', 'capacity')
    list_filter = ('congress', 'room')
    search_fields = ('title', 'speaker')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('participant', 'session', 'status', 'timestamp', 'staff')
    list_filter = ('status', 'session')
    search_fields = ('participant__name', 'session__title')

@admin.register(BadgePrintLog)
class BadgePrintLogAdmin(admin.ModelAdmin):
    list_display = ('registration', 'printed_by', 'printed_at')
    search_fields = ('registration__participant__name',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('action', 'details')

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    # Aquí es donde estaba el error, asegúrate de quitar 'institution'
    list_display = ('name', 'specialty', 'country', 'topic', 'congress')
    
    # Asegúrate de quitarlo de aquí también
    search_fields = ('name', 'specialty', 'country', 'topic')
    
    list_filter = ('congress', 'country')

@admin.register(ForumSpeaker)
class ForumSpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'country', 'topic', 'congress')
    search_fields = ('name', 'specialty', 'country', 'topic')
    list_filter = ('congress', 'country')