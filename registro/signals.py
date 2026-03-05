import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration, QRCode

# Esta señal "escucha" cada vez que se guarda un modelo Registration
@receiver(post_save, sender=Registration)
def create_qr_code(sender, instance, created, **kwargs):
    # Solo ejecutamos esto si es un registro NUEVO (no una actualización)
    if created:
        # 1. Creamos el objeto QRCode en la base de datos asociado a este registro.
        # Esto generará automáticamente el token UUID inhackeable.
        qr_obj = QRCode.objects.create(registration=instance)
        
        # 2. Configuramos y dibujamos la imagen del código QR usando la librería qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Metemos el token dentro del QR
        qr.add_data(str(qr_obj.token))
        qr.make(fit=True)

        # Generamos la imagen con colores clásicos
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 3. Guardamos la imagen en memoria y luego la adjuntamos al campo de la base de datos
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        # Le damos un nombre único al archivo basado en la cédula/ID del participante
        file_name = f'qr_{instance.participant.document_id}.png'
        
        # Guardamos el archivo físico asociado al objeto QRCode
        qr_obj.qr_image.save(file_name, ContentFile(buffer.getvalue()), save=True)