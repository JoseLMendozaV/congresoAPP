from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Congress, Participant, Registration, Session, QRCode, Attendance, Speaker
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required



@staff_member_required(login_url='/admin/login/')
def credencial(request, registro_id):
    registro_participante = get_object_or_404(Registration, id=registro_id)
    return render(request, 'credencial.html', {'registro': registro_participante})

# Nueva vista: Buscador para el Staff
@staff_member_required(login_url='/admin/login/')
def checkin_buscador(request):
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        # Busca por nombre, documento o correo
        resultados = Registration.objects.filter(
            Q(participant__name__icontains=query) |
            Q(participant__document_id__icontains=query) |
            Q(participant__email__icontains=query)
        ).select_related('participant', 'congress')
        
    return render(request, 'checkin.html', {'resultados': resultados, 'query': query})

# Nueva vista: Acción de marcar check-in
@staff_member_required(login_url='/admin/login/')
def hacer_checkin(request, registro_id):
    registro = get_object_or_404(Registration, id=registro_id)
    
    # Si no está acreditado aún, le cambiamos el estado
    if registro.status != 'ACCREDITED':
        registro.status = 'ACCREDITED'
        registro.save()
        
    # Redirigimos directamente a la pantalla de la credencial para imprimirla
    return redirect('credencial', registro_id=registro.id)


from django.http import JsonResponse
import json
from .models import Session, QRCode, Attendance

# Vista de la cámara y selección de charla
@staff_member_required(login_url='/admin/login/')
def control_sala(request):
    # Obtenemos todas las charlas para el menú desplegable
    charlas = Session.objects.all().order_by('start_time')
    return render(request, 'escanear.html', {'charlas': charlas})

# Endpoint que procesa el QR escaneado (AJAX)
@staff_member_required(login_url='/admin/login/')
def registrar_asistencia(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            session_id = data.get('session_id')

            if not token or not session_id:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos del escaneo.'})

            # 1. Validar que la charla exista
            charla = get_object_or_404(Session, id=session_id)

            # 2. Validar que el QR exista y esté vigente
            try:
                qr_obj = QRCode.objects.get(token=token, is_active=True)
            except QRCode.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'QR inválido o inactivo.'})

            registro = qr_obj.registration
            participante = registro.participant

            # 3. Validar que el participante tenga Check-in previo
            if registro.status != 'ACCREDITED':
                return JsonResponse({'status': 'warning', 'message': f'{participante.name} no ha hecho Check-in en registro.'})

            # 4. Evitar duplicado de asistencia en esta misma charla
            if Attendance.objects.filter(participant=participante, session=charla).exists():
                return JsonResponse({'status': 'warning', 'message': f'{participante.name} ya registró asistencia en esta charla.'})

            # 5. Registrar asistencia exitosa
            Attendance.objects.create(
                participant=participante,
                session=charla,
                staff=request.user if request.user.is_authenticated else None,
                status='APPROVED'
            )

            return JsonResponse({'status': 'success', 'message': f'¡Asistencia registrada para {participante.name}!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


import csv
from django.http import HttpResponse
from django.db.models import Count, Q
from .models import Registration, Session, Attendance

# Vista del Dashboard de Reportes
@staff_member_required(login_url='/admin/login/')
def reportes_dashboard(request):
    # 1. Acreditados vs No Acreditados
    total_registros = Registration.objects.count()
    acreditados = Registration.objects.filter(status='ACCREDITED').count()
    pre_registrados = Registration.objects.filter(status='PREREGISTERED').count()
    
    # 2. Asistencia por charla (totales)
    # Anotamos cada sesión con el conteo de asistencias 'APPROVED'
    charlas_stats = Session.objects.annotate(
        total_asistentes=Count('attendances', filter=Q(attendances__status='APPROVED'))
    ).order_by('start_time')

    context = {
        'total_registros': total_registros,
        'acreditados': acreditados,
        'pre_registrados': pre_registrados,
        'charlas_stats': charlas_stats,
    }
    return render(request, 'reportes.html', context)

# Vista para descargar el CSV de Asistencias
@staff_member_required(login_url='/admin/login/')
def exportar_asistencias_csv(request):
    # Configuramos la respuesta para que el navegador descargue un archivo
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="asistencias_congreso.csv"'

    # Creamos el escritor CSV
    writer = csv.writer(response)
    # Escribimos la fila de encabezados
    writer.writerow(['Charla', 'Participante', 'Documento', 'Estado Asistencia', 'Fecha/Hora', 'Staff'])

    # Obtenemos todas las asistencias optimizando las consultas con select_related
    asistencias = Attendance.objects.select_related('session', 'participant', 'staff').all().order_by('-timestamp')

    # Escribimos los datos fila por fila
    for asis in asistencias:
        staff_name = asis.staff.username if asis.staff else 'Sistema'
        writer.writerow([
            asis.session.title,
            asis.participant.name,
            asis.participant.document_id,
            asis.get_status_display(),
            asis.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            staff_name
        ])

    return response


from django.contrib import messages
from .models import Congress, Participant, Registration, Session, QRCode, Attendance

# ... mantén tus decoradores y otras importaciones arriba ...

# 1. Nueva Landing Page
def inicio(request):
    # Obtenemos el primer congreso de la base de datos para mostrarlo al público
    congreso = Congress.objects.first()
    
    # Obtenemos los conferencistas vinculados a ese congreso específico
    # (Si por alguna razón no hay congreso creado aún, enviamos una lista vacía)
    speakers = Speaker.objects.filter(congress=congreso) if congreso else []
    
    # Enviamos ambas variables a la plantilla HTML
    return render(request, 'inicio.html', {
        'congreso': congreso,
        'speakers': speakers
    })

# 2. Formulario de Registro Público
def registro_publico(request):
    congreso = Congress.objects.first()
    
    if not congreso:
        messages.error(request, "El congreso aún no ha sido configurado por el administrador.")
        return redirect('inicio')

    if request.method == 'POST':
        # Capturar datos del formulario
        name = request.POST.get('name')
        document_id = request.POST.get('document_id')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        is_utp = request.POST.get('is_utp') == 'on'
        utp_career = request.POST.get('utp_career') if is_utp else None
        
        # Manejar el año de curso (evitar error si viene vacío)
        utp_year_str = request.POST.get('utp_year')
        utp_year = int(utp_year_str) if is_utp and utp_year_str else None

        # Buscar o crear al participante (por si ya existía en la base de datos)
        participante, created = Participant.objects.get_or_create(
            document_id=document_id,
            defaults={
                'name': name, 'email': email, 'phone': phone,
                'is_utp': is_utp, 'utp_career': utp_career, 'utp_year': utp_year
            }
        )

        # Verificar si ya está inscrito en ESTE congreso para evitar duplicados
        if Registration.objects.filter(participant=participante, congress=congreso).exists():
            messages.warning(request, f"¡Hola {name}! Ya te encuentras registrado en este congreso.")
        else:
            # Creamos el registro con estado de Pre-registrado
            Registration.objects.create(
                participant=participante,
                congress=congreso,
                status='PREREGISTERED'
            )
            messages.success(request, f"¡Registro exitoso, {name}! Tu código QR ha sido generado. Acércate a la mesa de registro el día del evento.")
            return redirect('inicio')

    return render(request, 'registro_publico.html', {'congreso': congreso})