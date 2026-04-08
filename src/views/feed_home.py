from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from src.models import Publicacion, Usuario, Seguidor

@login_required
def feed_home(request):
    """
    Vista principal del feed con lógica de sugerencias real
    """
    # 1. Obtener IDs de usuarios que el usuario ya sigue
    ids_siguiendo = Seguidor.objects.filter(
        seguidor=request.user
    ).values_list('seguido_id', flat=True)

    # 2. Publicaciones para el feed
    publicaciones = Publicacion.objects.select_related(
        'autor'
    ).prefetch_related(
        'comentarios__autor'
    ).annotate(
        comentarios_count=Count('comentarios')
    ).order_by('-fecha_creacion')[:20]

    # 3. Sugerencias: Empresas que NO sigues y NO eres tú mismo
    suggested_users = Usuario.objects.filter(
        tipo_usuario='empresa'
    ).exclude(
        id__in=list(ids_siguiendo) + [request.user.id]
    ).select_related('empresa').order_by('?')[:5] # '?' para aleatoriedad

    # 4. Estadísticas del mini-perfil
    user_stats = {
        'followers_count': Seguidor.objects.filter(seguido=request.user).count(),
        'following_count': len(ids_siguiendo),
        'posts_count': request.user.publicaciones.count(),
    }
    
    context = {
        'publicaciones': publicaciones,
        'suggested_users': suggested_users,
        'user_stats': user_stats,
    }
    
    return render(request, 'feed_home.html', context)