from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Exists, OuterRef, Q
from django.utils.translation import gettext as _
from django.contrib import messages
from src.models import Publicacion, Comentario, Like, Seguidor, Usuario


@login_required
def feed_home(request):
    """
    Vista principal del feed
    """
    publicaciones = Publicacion.objects.select_related(
        'autor'
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_comentarios=Count('comentarios', distinct=True, filter=Q(comentarios__is_active=True)),
        usuario_dio_like=Exists(
            Like.objects.filter(
                publicacion=OuterRef('pk'),
                usuario=request.user
            )
        )
    ).order_by('-fecha_creacion')[:50]
    
    for pub in publicaciones:
        pub.usuario_sigue_autor = Seguidor.objects.filter(
            seguidor=request.user,
            seguido=pub.autor
        ).exists()
    
    context = {
        'publicaciones': publicaciones,
    }
    
    return render(request, 'feed/feed_home.html', context)


@login_required
def crear_publicacion(request):
    """
    Vista para crear una nueva publicación
    """
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        imagen = request.FILES.get('imagen')
        video = request.FILES.get('video')

        # Límite de 10 MB en bytes
        MAX_SIZE = 10 * 1024 * 1024

        # Validar tamaño de imagen
        if imagen and imagen.size > MAX_SIZE:
            messages.error(request, _('La imagen excede el límite permitido de 10MB.'))
            return redirect('feed_home')
            
        # Validar tamaño de video
        if video and video.size > MAX_SIZE:
            messages.error(request, _('El video excede el límite permitido de 10MB.'))
            return redirect('feed_home')
        
        if contenido or imagen or video:
            publicacion = Publicacion.objects.create(
                autor=request.user,
                contenido=contenido,
                imagen=imagen,
                video=video
            )
            messages.success(request, _('Publicación creada exitosamente.'))
            return redirect('feed_home')
    
    return redirect('feed_home')


@login_required
def toggle_like(request, publicacion_id):
    """
    Vista para dar/quitar like a una publicación
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    
    like, created = Like.objects.get_or_create(
        usuario=request.user,
        publicacion=publicacion
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    total_likes = publicacion.likes.count()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'total_likes': total_likes
    })


@login_required
def crear_comentario(request, publicacion_id):
    """
    Vista para crear un comentario (CON SOPORTE MULTIMEDIA)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    contenido = request.POST.get('contenido', '').strip()
    comentario_padre_id = request.POST.get('comentario_padre_id')
    
    # Obtener archivos multimedia
    imagen = request.FILES.get('imagen')
    video = request.FILES.get('video')
    
    # Validar que haya contenido o multimedia
    if not contenido and not imagen and not video:
        return JsonResponse({'error': 'Contenido vacío'}, status=400)
    
    comentario_padre = None
    if comentario_padre_id:
        comentario_padre = get_object_or_404(Comentario, id=comentario_padre_id)
    
    comentario = Comentario.objects.create(
        publicacion=publicacion,
        autor=request.user,
        contenido=contenido,
        comentario_padre=comentario_padre,
        imagen=imagen,
        video=video
    )
    
    return JsonResponse({
        'success': True,
        'comentario': {
            'id': comentario.id,
            'autor': comentario.autor.get_full_name(),
            'autor_avatar': comentario.autor.get_avatar_url(),
            'contenido': comentario.contenido,
            'nivel': comentario.get_nivel_visual(),
            'fecha': comentario.fecha_creacion.strftime('%d %b %Y'),
            'imagen': comentario.imagen.url if comentario.imagen else None,
            'video': comentario.video.url if comentario.video else None,
        },
        'total_comentarios': publicacion.comentarios.count()
    })


@login_required
def toggle_seguir(request, usuario_id):
    """
    Vista para seguir/dejar de seguir a un usuario
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    usuario_a_seguir = get_object_or_404(Usuario, id=usuario_id)
    
    if usuario_a_seguir == request.user:
        return JsonResponse({'error': 'No puedes seguirte a ti mismo'}, status=400)
    
    seguidor, created = Seguidor.objects.get_or_create(
        seguidor=request.user,
        seguido=usuario_a_seguir
    )
    
    if not created:
        seguidor.delete()
        siguiendo = False
    else:
        siguiendo = True
    
    return JsonResponse({
        'success': True,
        'siguiendo': siguiendo
    })


@login_required
def cargar_comentarios(request, publicacion_id):
    """
    Vista para cargar comentarios de una publicación (CON PAGINACIÓN)
    """
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    limit = int(request.GET.get('limit', 3))
    offset = int(request.GET.get('offset', 0))
    
    # Obtener comentarios de nivel 0 (raíz)
    comentarios_raiz = publicacion.comentarios.filter(
        comentario_padre__isnull=True
    ).select_related('autor').order_by('fecha_creacion')[offset:offset + limit]
    
    total_comentarios_raiz = publicacion.comentarios.filter(
        comentario_padre__isnull=True
    ).count()
    
    def serializar_comentario(comentario):
        return {
            'id': comentario.id,
            'autor': comentario.autor.get_full_name(),
            'autor_avatar': comentario.autor.get_avatar_url(),
            'contenido': comentario.contenido,
            'fecha': comentario.fecha_creacion.strftime('%d %b %Y'),
            'nivel': comentario.get_nivel_visual(),
            'imagen': comentario.imagen.url if comentario.imagen else None,
            'video': comentario.video.url if comentario.video else None,
            'total_respuestas': comentario.respuestas.count(),
            'respuestas': [serializar_comentario(resp) for resp in comentario.get_respuestas()]
        }
    
    comentarios_data = [serializar_comentario(c) for c in comentarios_raiz]
    
    return JsonResponse({
        'success': True,
        'comentarios': comentarios_data,
        'total': publicacion.comentarios.count(),
        'total_raiz': total_comentarios_raiz,
        'has_more': (offset + limit) < total_comentarios_raiz
    })