import uuid
from django.db import models
from django.contrib.auth.models import User

class Congress(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Congreso")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    location = models.CharField(max_length=200, verbose_name="Sede")

    def __str__(self):
        return self.name

class Participant(models.Model):
    CARRERAS_UTP = [
        ('ISC', 'Ingeniería de Sistemas Computacionales'),
        ('IC', 'Ingeniería Civil'),
        ('IE', 'Ingeniería Electromecánica'),
        ('II', 'Ingeniería Industrial'),
        ('OTRA', 'Otra'),
    ]

    name = models.CharField(max_length=150, verbose_name="Nombre completo")
    document_id = models.CharField(max_length=50, unique=True, verbose_name="Documento/ID")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    
    # Campos específicos para la UTP
    is_utp = models.BooleanField(default=False, verbose_name="¿Es de la UTP?")
    utp_career = models.CharField(max_length=10, choices=CARRERAS_UTP, blank=True, null=True, verbose_name="Carrera UTP")
    utp_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año de curso")

    def __str__(self):
        return f"{self.name} ({self.document_id})"

class Registration(models.Model):
    STATUS_CHOICES = [
        ('PREREGISTERED', 'Pre-registrado'),
        ('ACCREDITED', 'Acreditado (Check-in)'),
        ('CANCELED', 'Cancelado'),
    ]

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='registrations')
    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREREGISTERED')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant', 'congress')

    def __str__(self):
        return f"{self.participant.name} - {self.congress.name}"

class QRCode(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='qr_code')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.token)

class Session(models.Model):
    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200, verbose_name="Título de la charla")
    speaker = models.CharField(max_length=150, verbose_name="Ponente")
    room = models.CharField(max_length=100, verbose_name="Sala")
    start_time = models.DateTimeField(verbose_name="Inicio")
    end_time = models.DateTimeField(verbose_name="Fin")
    capacity = models.PositiveIntegerField(verbose_name="Cupo máximo")
    description = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.title

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='attendances')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    timestamp = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='APPROVED')
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Motivo de rechazo/duplicado")

    class Meta:
        unique_together = ('participant', 'session')

class BadgePrintLog(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='print_logs')
    printed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    printed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Motivo (si es reimpresión)")

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)


class Speaker(models.Model):

    PAISES_CHOICES = [
        ('pa', 'Panamá'),
        ('co', 'Colombia'),
        ('cr', 'Costa Rica'),
        ('mx', 'México'),
        ('es', 'España'),
        ('ar', 'Argentina'),
        ('cl', 'Chile'),
        ('pe', 'Perú'),
        ('us', 'Estados Unidos'),
        ('br', 'Brasil'),
        ('de', 'Alemania'),
        ('uy', 'Uruguay'),

    ]



    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='speakers', verbose_name="Congreso")
    name = models.CharField(max_length=150, verbose_name="Nombre del Conferencista")
    specialty = models.CharField(max_length=200, verbose_name="Especialidad")
    topic = models.CharField(max_length=200, verbose_name="Tema a exponer")
    country = models.CharField(max_length=2, choices=PAISES_CHOICES, default='pa', verbose_name="País")
    photo = models.ImageField(upload_to='speakers/', blank=True, null=True, verbose_name="Foto de perfil")

    def __str__(self):
        return self.name
    

class ForumSpeaker(models.Model):
    PAISES_CHOICES = [
        ('pa', 'Panamá'),
        ('co', 'Colombia'),
        ('cr', 'Costa Rica'),
        ('mx', 'México'),
        ('es', 'España'),
        ('ar', 'Argentina'),
        ('cl', 'Chile'),
        ('pe', 'Perú'),
        ('us', 'Estados Unidos'),
        ('br', 'Brasil'),
        ('de', 'Alemania'),
        ('uy', 'Uruguay'),
    ]

    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='forum_speakers', verbose_name="Congreso")
    name = models.CharField(max_length=150, verbose_name="Nombre del Panelista")
    specialty = models.CharField(max_length=200, verbose_name="Especialidad")
    topic = models.CharField(max_length=200, verbose_name="Tema del Foro")
    country = models.CharField(max_length=2, choices=PAISES_CHOICES, default='pa', verbose_name="País")
    photo = models.ImageField(upload_to='forum_speakers/', blank=True, null=True, verbose_name="Foto de perfil")

    def __str__(self):
        return self.name