from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Count
from django.utils.translation import gettext as _
from src.models import Conversacion, Mensaje, Usuario

@login_required
def message_list(request):
    """
    Vista principal de mensajería
    Lista todas las conversaciones del usuario
    """
    user = request.user
    
    # Obtener todas las conversaciones del usuario
    conversaciones = Conversacion.objects.filter(
        Q(participante_1=user) | Q(participante_2=user)
    ).annotate(
        ultimo_mensaje_fecha=Max('mensajes__fecha_envio')
    ).order_by('-ultimo_mensaje_fecha')
    
    # Preparar datos de conversaciones
    conversaciones_data = []
    for conv in conversaciones:
        otro_usuario = conv.get_otro_participante(user)
        ultimo_mensaje = conv.get_ultimo_mensaje()
        no_leidos = conv.mensajes_no_leidos(user)
        
        conversaciones_data.append({
            'conversacion': conv,
            'otro_usuario': otro_usuario,
            'ultimo_mensaje': ultimo_mensaje,
            'no_leidos': no_leidos,
        })
    
    context = {
        'conversaciones_data': conversaciones_data,
    }
    
    return render(request, 'messages/message_list.html', context)