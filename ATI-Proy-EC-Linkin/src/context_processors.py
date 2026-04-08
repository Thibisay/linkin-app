from src.models import Notificacion

def notifications_processor(request):
    """
    Context processor para hacer disponibles las notificaciones en todos los templates
    """
    if request.user.is_authenticated:
        # Obtener notificaciones no leídas
        notificaciones_no_leidas = Notificacion.objects.filter(
            destinatario=request.user,
            leida=False
        ).count()
        
        # Obtener las 5 notificaciones más recientes
        notificaciones_recientes = Notificacion.objects.filter(
            destinatario=request.user
        ).select_related('emisor').order_by('-fecha_creacion')[:5]
        
        return {
            'notificaciones_count': notificaciones_no_leidas,
            'notificaciones_recientes': notificaciones_recientes,
        }
    
    return {
        'notificaciones_count': 0,
        'notificaciones_recientes': [],
    }