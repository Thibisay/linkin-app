from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from src.models import OfertaEmpleo, EmpleoGuardado, Profesional, Postulacion
from src.filters import OfertaEmpleoFilter

"""
Vistas para el sistema de empleos
IMPORTANTE: Este archivo usa EmpleoGuardado SEPARADO de Postulacion
- EmpleoGuardado: Para guardar empleos como favoritos (sin aplicar)
- Postulacion: Para aplicar a empleos (con todos los datos)
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from src.models import OfertaEmpleo, Postulacion, EmpleoGuardado


def job_detail(request, job_id):
    """
    Vista de detalle de una oferta de empleo
    """
    # Para empresas: permitir ver sus propias ofertas (activas o inactivas)
    # Para profesionales: solo ver ofertas activas de otras empresas
    if request.user.is_authenticated and request.user.tipo_usuario == 'empresa':
        oferta = get_object_or_404(
            OfertaEmpleo.objects.select_related('empresa__user'),
            Q(id=job_id) & (Q(activa=True) | Q(empresa=request.user.empresa))
        )
    else:
        oferta = get_object_or_404(
            OfertaEmpleo.objects.select_related('empresa__user'),
            id=job_id,
            activa=True
        )
    
    # Incrementar vistas solo si NO es la empresa dueña
    if not (request.user.is_authenticated and 
            request.user.tipo_usuario == 'empresa' and 
            oferta.empresa == request.user.empresa):
        oferta.vistas += 1
        oferta.save(update_fields=['vistas'])
    
    # Verificar si el usuario ya postuló Y si está guardado (SEPARADOS)
    ya_postulo = False
    esta_guardado = False
    
    if request.user.is_authenticated and request.user.tipo_usuario == 'profesional':
        profesional = request.user.profesional
        
        # SEPARADO 1: Verificar si YA APLICÓ (Postulacion)
        ya_postulo = Postulacion.objects.filter(
            oferta=oferta,
            profesional=profesional
        ).exists()
        
        # SEPARADO 2: Verificar si está GUARDADO (EmpleoGuardado)
        esta_guardado = EmpleoGuardado.objects.filter(
            oferta=oferta,
            profesional=profesional
        ).exists()
    
    # Ofertas similares (solo activas)
    ofertas_similares = OfertaEmpleo.objects.filter(
        activa=True,
        nivel=oferta.nivel
    ).exclude(
        id=oferta.id
    ).select_related('empresa__user')[:5]
    
    context = {
        'oferta': oferta,
        'ya_postulo': ya_postulo,
        'esta_guardado': esta_guardado,
        'ofertas_similares': ofertas_similares,
    }
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_apply(request, job_id):
    """
    Aplicar a una oferta de empleo - SOLO crea Postulacion con todos los datos
    """
    # Verificar que sea profesional
    if request.user.tipo_usuario != 'profesional':
        return JsonResponse({
            'success': False,
            'error': _('Solo profesionales pueden aplicar a ofertas')
        }, status=403)
    
    oferta = get_object_or_404(OfertaEmpleo, id=job_id, activa=True)
    profesional = request.user.profesional
    
    # Verificar si ya aplicó
    if Postulacion.objects.filter(
        profesional=profesional,
        oferta=oferta
    ).exists():
        return JsonResponse({
            'success': False,
            'error': _('Ya has aplicado a esta oferta')
        }, status=400)
    
    if request.method == 'POST':
        try:
            # VALIDAR TODOS LOS CAMPOS REQUERIDOS
            habilidades = request.POST.get('habilidades_tecnicas', '').strip()
            anos_experiencia = request.POST.get('anos_experiencia', '').strip()
            nivel_habilidad = request.POST.get('nivel_habilidad', '').strip()
            telefono = request.POST.get('telefono_contacto', '').strip()
            email = request.POST.get('email_contacto', '').strip()
            curriculum = request.FILES.get('curriculum')
            
            # VALIDACIÓN 1: Habilidades técnicas
            if not habilidades:
                return JsonResponse({
                    'success': False,
                    'error': _('Las habilidades técnicas son requeridas')
                }, status=400)
            
            # VALIDACIÓN 2: Años de experiencia
            if not anos_experiencia:
                return JsonResponse({
                    'success': False,
                    'error': _('Los años de experiencia son requeridos')
                }, status=400)
            
            try:
                anos_experiencia = int(anos_experiencia)
                if anos_experiencia < 0:
                    return JsonResponse({
                        'success': False,
                        'error': _('Los años de experiencia deben ser mayor o igual a 0')
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': _('Los años de experiencia deben ser un número válido')
                }, status=400)
            
            # VALIDACIÓN 3: Nivel de habilidad
            if not nivel_habilidad or nivel_habilidad not in ['junior', 'mid', 'senior']:
                return JsonResponse({
                    'success': False,
                    'error': _('El nivel de habilidad es requerido')
                }, status=400)
            
            # VALIDACIÓN 4: Teléfono
            if not telefono or len(telefono) < 10:
                return JsonResponse({
                    'success': False,
                    'error': _('El teléfono debe tener al menos 10 caracteres')
                }, status=400)
            
            # VALIDACIÓN 5: Email
            if not email or '@' not in email:
                return JsonResponse({
                    'success': False,
                    'error': _('El email es requerido y debe ser válido')
                }, status=400)
            
            # VALIDACIÓN 6: Currículum
            if not curriculum:
                return JsonResponse({
                    'success': False,
                    'error': _('El currículum es requerido')
                }, status=400)
            
            # Validar tamaño del archivo (máximo 5MB)
            if curriculum.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': _('El currículum no debe superar 5MB')
                }, status=400)
            
            # Validar formato del archivo
            allowed_extensions = ['.pdf', '.doc', '.docx']
            if not any(curriculum.name.lower().endswith(ext) for ext in allowed_extensions):
                return JsonResponse({
                    'success': False,
                    'error': _('Solo se permiten archivos PDF, DOC o DOCX')
                }, status=400)
            
            # TODO VALIDADO - Crear postulación
            postulacion = Postulacion.objects.create(
                profesional=profesional,
                oferta=oferta,
                habilidades_tecnicas=habilidades,
                anos_experiencia=anos_experiencia,
                nivel_habilidad=nivel_habilidad,
                telefono_contacto=telefono,
                email_contacto=email,
                curriculum=curriculum,
                estado='en_revision'  # Estado inicial
            )
            
            return JsonResponse({
                'success': True,
                'message': _('¡Aplicación enviada exitosamente!'),
                'redirect': f'/jobs/{job_id}/'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': _('Hubo un error al enviar tu aplicación: ') + str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': _('Método no permitido')
    }, status=405)


@login_required
def guardar_empleo(request, job_id):
    """
    Guardar o quitar de guardados un empleo - USA EmpleoGuardado, NO Postulacion
    """
    # Verificar que sea profesional
    if request.user.tipo_usuario != 'profesional':
        return JsonResponse({
            'success': False,
            'error': _('Solo profesionales pueden guardar empleos')
        }, status=403)
    
    profesional = request.user.profesional
    oferta = get_object_or_404(OfertaEmpleo, id=job_id, activa=True)
    
    # Verificar si ya está guardado en EmpleoGuardado (NO en Postulacion)
    empleo_guardado = EmpleoGuardado.objects.filter(
        profesional=profesional,
        oferta=oferta
    ).first()
    
    if empleo_guardado:
        # Si ya está guardado, eliminarlo
        empleo_guardado.delete()
        return JsonResponse({
            'success': True,
            'guardado': False,
            'message': _('Empleo removido de guardados')
        })
    else:
        # Si no está guardado, guardarlo (sin crear Postulacion)
        EmpleoGuardado.objects.create(
            profesional=profesional,
            oferta=oferta
        )
        return JsonResponse({
            'success': True,
            'guardado': True,
            'message': _('Empleo guardado exitosamente')
        })


@login_required
def empleos_guardados(request):
    """
    Lista de empleos guardados por el profesional - USA EmpleoGuardado
    """
    # Verificar que sea profesional
    if request.user.tipo_usuario != 'profesional':
        messages.error(request, _('Solo los profesionales pueden guardar empleos'))
        return redirect('feed_home')
    
    profesional = request.user.profesional
    
    # Obtener empleos guardados desde EmpleoGuardado (NO desde Postulacion)
    empleos_guardados = EmpleoGuardado.objects.filter(
        profesional=profesional,
        oferta__activa=True  # Solo mostrar ofertas activas
    ).select_related(
        'oferta__empresa__user'
    ).order_by('-fecha_guardado')
    
    # Paginación
    paginator = Paginator(empleos_guardados, 20)
    page_num = request.GET.get('page', 1)
    empleos_page = paginator.get_page(page_num)
    
    # Obtener IDs de empleos a los que ya aplicó (desde Postulacion)
    empleos_aplicados = list(
        Postulacion.objects.filter(
            profesional=profesional
        ).values_list('oferta_id', flat=True)
    )
    
    context = {
        'empleos_guardados': empleos_page,
        'empleos_aplicados': empleos_aplicados,
        'total_guardados': empleos_guardados.count(),
    }
    
    return render(request, 'jobs/empleos_guardados.html', context)

@login_required
def busqueda_avanzada_empleos(request):
    """
    Búsqueda avanzada de empleos con múltiples filtros
    """
    # Obtener ofertas activas
    queryset = OfertaEmpleo.objects.filter(activa=True).select_related('empresa__user')
    
    # Aplicar filtros
    filtro = OfertaEmpleoFilter(request.GET, queryset=queryset)
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_publicacion')
    ofertas_filtradas = filtro.qs.order_by(orden)
    
    # Si es profesional, obtener IDs de empleos guardados y aplicados
    empleos_guardados_ids = []
    empleos_aplicados_ids = []
    
    if request.user.tipo_usuario == 'profesional':
        profesional = request.user.profesional
        empleos_guardados_ids = list(
            EmpleoGuardado.objects.filter(
                profesional=profesional
            ).values_list('oferta_id', flat=True)
        )
        empleos_aplicados_ids = list(
            Postulacion.objects.filter(
                profesional=profesional
            ).values_list('oferta_id', flat=True)
        )
    
    # Paginación
    paginator = Paginator(ofertas_filtradas, 20)
    page_num = request.GET.get('page', 1)
    ofertas_page = paginator.get_page(page_num)
    
    # Contar resultados por categoría
    resultados_por_modalidad = filtro.qs.values('modalidad').annotate(
        count=Count('id')
    )
    
    resultados_por_tipo = filtro.qs.values('tipo_empleo').annotate(
        count=Count('id')
    )
    
    context = {
        'filter': filtro,
        'ofertas': ofertas_page,
        'total_results': filtro.qs.count(),
        'empleos_guardados_ids': empleos_guardados_ids,
        'empleos_aplicados_ids': empleos_aplicados_ids,
        'resultados_por_modalidad': resultados_por_modalidad,
        'resultados_por_tipo': resultados_por_tipo,
        'query': request.GET.get('q', ''),
    }
    
    return render(request, 'search/busqueda_empleos.html', context)