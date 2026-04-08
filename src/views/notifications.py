from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from src.models import Notificacion

@login_required
def notifications_list(request):
    """
    Lista de notificaciones del usuario
    """
    # Obtener todas las notificaciones del usuario
    notificaciones = Notificacion.objects.filter(
        destinatario=request.user
    ).select_related('emisor').order_by('-fecha_creacion')
    
    # Filtrar por leídas/no leídas
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notificaciones = notificaciones.filter(leida=False)
    elif filter_type == 'read':
        notificaciones = notificaciones.filter(leida=True)
    
    # Paginación
    paginator = Paginator(notificaciones, 20)
    page_num = request.GET.get('page', 1)
    notificaciones_page = paginator.get_page(page_num)
    
    # Contar no leídas
    total_no_leidas = Notificacion.objects.filter(
        destinatario=request.user,
        leida=False
    ).count()
    
    context = {
        'notificaciones': notificaciones_page,
        'total_no_leidas': total_no_leidas,
        'filter_type': filter_type,
    }
    
    return render(request, 'notifications/notifications_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """
    Marca una notificación como leída
    """
    notificacion = get_object_or_404(
        Notificacion,
        id=notification_id,
        destinatario=request.user
    )
    
    notificacion.marcar_como_leida()
    
    # Redirigir a la URL de la notificación o al origen
    if notificacion.url:
        return redirect(notificacion.url)
    
    return redirect('notifications_list')


@login_required
def mark_all_as_read(request):
    """
    Marca todas las notificaciones como leídas
    """
    if request.method == 'POST':
        Notificacion.objects.filter(
            destinatario=request.user,
            leida=False
        ).update(leida=True)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def get_notifications_count(request):
    """
    API endpoint para obtener el contador de notificaciones no leídas
    """
    count = Notificacion.objects.filter(
        destinatario=request.user,
        leida=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def delete_notification(request, notification_id):
    """
    Elimina (desactiva) una notificación
    """
    if request.method == 'POST':
        notificacion = get_object_or_404(
            Notificacion,
            id=notification_id,
            destinatario=request.user
        )
        
        notificacion.activa = False
        notificacion.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)