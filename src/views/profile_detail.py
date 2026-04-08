from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from src.models import Usuario, Profesional, Empresa, Seguidor

@login_required
def profile_detail(request, user_id):
    """
    Vista unificada para ver perfiles (Profesional o Empresa)
    """
    profile_user = get_object_or_404(Usuario, id=user_id)
    is_own_profile = request.user.id == profile_user.id
    
    # Lógica de seguidores
    esta_siguiendo = False
    if request.user.is_authenticated and not is_own_profile:
        esta_siguiendo = Seguidor.objects.filter(
            seguidor=request.user, 
            seguido=profile_user
        ).exists()
    
    # Estadísticas básicas
    total_seguidores = Seguidor.objects.filter(seguido=profile_user).count()
    total_siguiendo = Seguidor.objects.filter(seguidor=profile_user).count()
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'esta_siguiendo': esta_siguiendo,
        'total_seguidores': total_seguidores,
        'total_siguiendo': total_siguiendo,
        'total_conexiones': total_seguidores, # Lógica simplificada
    }

    # 1. PERFIL PROFESIONAL
    if profile_user.tipo_usuario == 'profesional':
        profesional = get_object_or_404(Profesional, user=profile_user)
        context.update({
            'profesional': profesional,
            'experiencias': profesional.experiencias.all().order_by('-fecha_inicio')[:5],
            'educaciones': profesional.educaciones.all().order_by('-fecha_inicio')[:5],
            'habilidades': profesional.habilidades.all(),
        })
        return render(request, 'profiles/profesional_detail.html', context)
    
    # 2. PERFIL EMPRESA
    elif profile_user.tipo_usuario == 'empresa':
        empresa = get_object_or_404(Empresa, user=profile_user)
        # Aquí irían las ofertas activas cuando tengas el modelo
        # ofertas = empresa.ofertas.filter(activa=True)[:5]
        context.update({
            'empresa': empresa,
            # 'ofertas': ofertas
        })
        return render(request, 'profiles/empresa_detail.html', context)
    
    return redirect('feed_home')


@login_required
def profile_edit(request, user_id):
    """
    Vista unificada para editar perfil.
    Maneja la carga de imágenes (foto) y datos según el tipo de usuario.
    """
    # Seguridad: Solo el dueño puede editar
    if request.user.id != int(user_id):
        messages.error(request, _('No tienes permiso para editar este perfil'))
        return redirect('profile_detail', user_id=user_id)
    
    user = request.user

    if request.method == 'POST':
        # 1. Actualizar datos base del Usuario (Común para ambos)
        # Usamos request.POST.get para evitar errores si el campo no viene
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.ubicacion = request.POST.get('ubicacion', user.ubicacion)
        
        # 2. Manejo de Imagen (Avatar/Logo)
        # Importante: El input en el HTML debe llamarse 'foto'
        if 'foto' in request.FILES:
            user.foto = request.FILES['foto']
        
        user.save()

        # 3. Actualización Específica por Rol
        if user.tipo_usuario == 'profesional':
            profesional = get_object_or_404(Profesional, user=user)
            profesional.titulo_actual = request.POST.get('titulo_actual', '')
            profesional.descripcion_personal = request.POST.get('descripcion_personal', '')
            profesional.cedula = request.POST.get('cedula', '')
            
            fecha_nac = request.POST.get('fecha_nacimiento')
            if fecha_nac:
                profesional.fecha_nacimiento = fecha_nac
            
            profesional.genero = request.POST.get('genero', '')
            profesional.linkedin_url = request.POST.get('linkedin_url', '')
            profesional.github_url = request.POST.get('github_url', '')
            profesional.portfolio_url = request.POST.get('portfolio_url', '')
            profesional.save()

        elif user.tipo_usuario == 'empresa':
            empresa = get_object_or_404(Empresa, user=user)
            empresa.nombre_empresa = request.POST.get('nombre_empresa', '')
            empresa.descripcion_breve = request.POST.get('descripcion_breve', '')
            empresa.descripcion_completa = request.POST.get('descripcion_completa', '')
            empresa.rif = request.POST.get('rif', '')
            empresa.sector = request.POST.get('sector', '')
            empresa.tamano = request.POST.get('tamano', '')
            empresa.sitio_web = request.POST.get('sitio_web', '')
            empresa.telefono = request.POST.get('telefono', '')
            empresa.email_contacto = request.POST.get('email_contacto', '')
            # Redes sociales
            empresa.linkedin_url = request.POST.get('linkedin_url', '')
            empresa.facebook_url = request.POST.get('facebook_url', '')
            empresa.instagram_url = request.POST.get('instagram_url', '')
            empresa.save()

        messages.success(request, _('Perfil actualizado exitosamente'))
        return redirect('profile_detail', user_id=user.id)

    # GET Request: Renderizar templates con datos actuales
    if user.tipo_usuario == 'profesional':
        context = {
            'user': user,
            'profesional': user.profesional
        }
        return render(request, 'profiles/profesional_edit.html', context)
    
    elif user.tipo_usuario == 'empresa':
        context = {
            'user': user,
            'empresa': user.empresa
        }
        return render(request, 'profiles/empresa_edit.html', context)

    return redirect('feed_home')