from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from src.models import Usuario

@login_required
def search_users(request):
    """
    API endpoint para buscar usuarios
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    # Buscar usuarios excluyendo el usuario actual
    usuarios = Usuario.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(
        id=request.user.id
    )[:10]
    
    users_data = []
    for user in usuarios:
        title = ''
        if user.tipo_usuario == 'profesional' and hasattr(user, 'profesional'):
            title = user.profesional.titulo_actual or 'Profesional'
        elif user.tipo_usuario == 'empresa' and hasattr(user, 'empresa'):
            title = user.empresa.nombre_empresa or 'Empresa'
        
        users_data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'title': title,
            'avatar': user.get_avatar_url(),
        })
    
    return JsonResponse({'users': users_data})