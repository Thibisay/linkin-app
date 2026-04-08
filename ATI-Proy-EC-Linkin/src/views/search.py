from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from src.models import Usuario, Publicacion, OfertaEmpleo, Profesional, Empresa
from src.filters import OfertaEmpleoFilter, ProfesionalFilter


@login_required
def search_general(request):
    """
    Búsqueda general: usuarios, publicaciones y trabajos
    """
    query = request.GET.get('q', '').strip()
    tab = request.GET.get('tab', 'all')  # all, users, posts, jobs
    
    context = {
        'query': query,
        'tab': tab,
    }
    
    if not query:
        return render(request, 'search/search_results.html', context)
    
    # Búsqueda de usuarios (profesionales y empresas)
    usuarios = Usuario.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)
    
    # Añadir información específica según tipo
    usuarios = usuarios.select_related('profesional', 'empresa')
    
    # Búsqueda de publicaciones
    publicaciones = Publicacion.objects.filter(
        is_active=True
    ).filter(
        Q(contenido__icontains=query) |
        Q(autor__first_name__icontains=query) |
        Q(autor__last_name__icontains=query)
    ).select_related('autor').annotate(
        num_likes=Count('likes', distinct=True),
        num_comentarios=Count('comentarios', distinct=True)
    ).order_by('-fecha_creacion')
    
    # Búsqueda de trabajos
    trabajos = OfertaEmpleo.objects.filter(
        activa=True
    ).filter(
        Q(titulo__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(empresa__nombre_empresa__icontains=query)
    ).select_related('empresa__user').annotate(
        num_postulaciones=Count('postulaciones', distinct=True)
    ).order_by('-fecha_publicacion')
    
    # Filtrar según tab
    if tab == 'users':
        publicaciones = Publicacion.objects.none()
        trabajos = OfertaEmpleo.objects.none()
    elif tab == 'posts':
        usuarios = Usuario.objects.none()
        trabajos = OfertaEmpleo.objects.none()
    elif tab == 'jobs':
        usuarios = Usuario.objects.none()
        publicaciones = Publicacion.objects.none()
    
    # Paginación
    usuarios_paginator = Paginator(usuarios, 10)
    publicaciones_paginator = Paginator(publicaciones, 10)
    trabajos_paginator = Paginator(trabajos, 10)
    
    page_num = request.GET.get('page', 1)
    
    usuarios_page = usuarios_paginator.get_page(page_num)
    publicaciones_page = publicaciones_paginator.get_page(page_num)
    trabajos_page = trabajos_paginator.get_page(page_num)
    
    context.update({
        'usuarios': usuarios_page,
        'publicaciones': publicaciones_page,
        'trabajos': trabajos_page,
        'total_usuarios': usuarios.count(),
        'total_publicaciones': publicaciones.count(),
        'total_trabajos': trabajos.count(),
    })
    
    return render(request, 'search/search_results.html', context)


@login_required
def search_jobs(request):
    """
    Búsqueda de empleos con filtros
    """
    # Obtener solo ofertas activas
    queryset = OfertaEmpleo.objects.filter(activa=True).select_related('empresa__user')
    
    # Aplicar filtros
    filtro = OfertaEmpleoFilter(request.GET, queryset=queryset)
    
    # Paginación
    paginator = Paginator(filtro.qs, 20)
    page_num = request.GET.get('page', 1)
    ofertas_page = paginator.get_page(page_num)
    
    context = {
        'filter': filtro,
        'ofertas': ofertas_page,
        'total_results': filtro.qs.count(),
    }
    
    return render(request, 'search/search_jobs.html', context)


@login_required
def search_talent(request):
    """
    Búsqueda de talento (solo para empresas)
    """
    # Verificar que sea empresa
    if request.user.tipo_usuario != 'empresa':
        from django.contrib import messages
        messages.error(request, _('Solo las empresas pueden buscar talento'))
        from django.shortcuts import redirect
        return redirect('feed_home')
    
    # Obtener profesionales activos
    queryset = Profesional.objects.filter(
        user__is_active=True
    ).select_related('user').prefetch_related('habilidades', 'experiencias')
    
    # Aplicar filtros
    filtro = ProfesionalFilter(request.GET, queryset=queryset)
    
    # Paginación
    paginator = Paginator(filtro.qs, 20)
    page_num = request.GET.get('page', 1)
    profesionales_page = paginator.get_page(page_num)
    
    context = {
        'filter': filtro,
        'profesionales': profesionales_page,
        'total_results': filtro.qs.count(),
    }
    
    return render(request, 'search/search_talent.html', context)