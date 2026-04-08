from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils.translation import gettext as _
from django.contrib import messages
from src.models import Conversacion, Mensaje, Usuario

@login_required
def message_detail(request, conversation_id):
    """
    Vista de detalle de una conversación
    """
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    otro_usuario = conversacion.get_otro_participante(request.user)
    
    # Verificar si está bloqueada
    es_bloqueada = conversacion.estado == 'bloqueada'
    bloqueada_por_mi = conversacion.bloqueado_por == request.user
    
    # Verificar si es una solicitud pendiente
    es_solicitud_pendiente = (
        conversacion.estado == 'pendiente' and 
        conversacion.participante_2 == request.user
    )
    
    # Obtener todos los mensajes
    mensajes = conversacion.mensajes.select_related('emisor', 'receptor').all()
    
    # Marcar mensajes como leídos solo si la conversación está aceptada
    if conversacion.estado == 'aceptada':
        mensajes_no_leidos = mensajes.filter(receptor=request.user, leido=False)
        for mensaje in mensajes_no_leidos:
            mensaje.marcar_como_leido()
    
    # Obtener todas las conversaciones para el sidebar
    conversaciones = Conversacion.objects.filter(
        Q(participante_1=request.user) | Q(participante_2=request.user)
    ).order_by('-fecha_actualizacion')
    
    conversaciones_data = []
    for conv in conversaciones:
        otro_usuario_conv = conv.get_otro_participante(request.user)
        ultimo_mensaje = conv.get_ultimo_mensaje()
        no_leidos = conv.mensajes_no_leidos(request.user)
        
        conversaciones_data.append({
            'conversacion': conv,
            'otro_usuario': otro_usuario_conv,
            'ultimo_mensaje': ultimo_mensaje,
            'no_leidos': no_leidos,
        })
    
    # Media compartida
    media_compartida = conversacion.mensajes.exclude(archivo='').order_by('-fecha_envio')[:6]
    
    context = {
        'conversacion': conversacion,
        'otro_usuario': otro_usuario,
        'mensajes': mensajes,
        'media_compartida': media_compartida,
        'conversaciones_data': conversaciones_data,
        'es_bloqueada': es_bloqueada,
        'bloqueada_por_mi': bloqueada_por_mi,
        'es_solicitud_pendiente': es_solicitud_pendiente,
    }
    
    return render(request, 'messages/message_detail.html', context)


@login_required
def send_message(request, conversation_id):
    """
    Enviar un mensaje
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    # Verificar si puede enviar mensajes
    if not conversacion.puede_enviar_mensaje(request.user):
        return JsonResponse({
            'success': False,
            'error': _('No puedes enviar mensajes en esta conversación')
        }, status=403)
    
    contenido = request.POST.get('contenido', '').strip()
    
    if not contenido:
        return JsonResponse({'success': False, 'error': 'Empty message'}, status=400)
    
    otro_usuario = conversacion.get_otro_participante(request.user)
    
    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        emisor=request.user,
        receptor=otro_usuario,
        contenido=contenido,
        archivo=request.FILES.get('archivo')
    )
    
    # Actualizar conversación
    conversacion.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': {
            'id': mensaje.id,
            'contenido': mensaje.contenido,
            'emisor_id': mensaje.emisor.id,
            'emisor_nombre': mensaje.emisor.get_full_name(),
            'emisor_avatar': mensaje.emisor.get_avatar_url(),
            'fecha': mensaje.fecha_envio.strftime('%H:%M'),
        }
    })


@login_required
def accept_conversation(request, conversation_id):
    """
    Aceptar una solicitud de conversación
    """
    if request.method != 'POST':
        return redirect('message_detail', conversation_id=conversation_id)
    
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    # Verificar que sea el receptor y esté pendiente
    if conversacion.participante_2 == request.user and conversacion.estado == 'pendiente':
        conversacion.estado = 'aceptada'
        conversacion.save()
        messages.success(request, _('Solicitud aceptada'))
    
    return redirect('message_detail', conversation_id=conversation_id)


@login_required
def reject_conversation(request, conversation_id):
    """
    Rechazar una solicitud de conversación
    """
    if request.method != 'POST':
        return redirect('message_list')
    
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    # Verificar que sea el receptor y esté pendiente
    if conversacion.participante_2 == request.user and conversacion.estado == 'pendiente':
        conversacion.estado = 'rechazada'
        conversacion.save()
        messages.success(request, _('Solicitud rechazada'))
    
    return redirect('message_list')


@login_required
def block_conversation(request, conversation_id):
    """
    Bloquear una conversación
    """
    if request.method != 'POST':
        return redirect('message_detail', conversation_id=conversation_id)
    
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    conversacion.estado = 'bloqueada'
    conversacion.bloqueado_por = request.user
    conversacion.save()
    
    messages.success(request, _('Usuario bloqueado'))
    return redirect('message_list')


@login_required
def unblock_conversation(request, conversation_id):
    """
    Desbloquear una conversación
    """
    if request.method != 'POST':
        return redirect('message_detail', conversation_id=conversation_id)
    
    conversacion = get_object_or_404(
        Conversacion,
        Q(participante_1=request.user) | Q(participante_2=request.user),
        id=conversation_id
    )
    
    if conversacion.bloqueado_por == request.user:
        conversacion.estado = 'aceptada'
        conversacion.bloqueado_por = None
        conversacion.save()
        messages.success(request, _('Usuario desbloqueado'))
    
    return redirect('message_detail', conversation_id=conversation_id)


@login_required
def create_conversation(request, user_id):
    """
    Crear una nueva conversación o redirigir a existente
    """
    otro_usuario = get_object_or_404(Usuario, id=user_id)
    
    if otro_usuario == request.user:
        return redirect('message_list')
    
    # Buscar conversación existente (en cualquier dirección)
    conversacion = Conversacion.objects.filter(
        Q(participante_1=request.user, participante_2=otro_usuario) |
        Q(participante_1=otro_usuario, participante_2=request.user)
    ).first()
    
    if not conversacion:
        conversacion = Conversacion.objects.create(
            participante_1=request.user,
            participante_2=otro_usuario,
            estado='pendiente'
        )
    
    return redirect('message_detail', conversation_id=conversacion.id)