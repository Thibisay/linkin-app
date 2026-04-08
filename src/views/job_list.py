# src/views/jobs.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from src.models import OfertaEmpleo, Postulacion, EmpleoGuardado

@login_required
def job_list(request):
    user = request.user

    if user.tipo_usuario == 'empresa':
        # Empresa: ver sus propias ofertas (activas e inactivas)
        ofertas_activas = user.empresa.ofertas.filter(
            activa=True
        ).annotate(
            postulaciones_count=Count('postulaciones')
        ).order_by('-fecha_publicacion')

        ofertas_inactivas = user.empresa.ofertas.filter(
            activa=False
        ).annotate(
            postulaciones_count=Count('postulaciones')
        ).order_by('-fecha_publicacion')

        total_postulaciones = Postulacion.objects.filter(
            oferta__empresa=user.empresa
        ).count()

        context = {
            'ofertas_activas': ofertas_activas,
            'ofertas_inactivas': ofertas_inactivas,
            'total_postulaciones': total_postulaciones,
            'user_type': 'empresa',
        }
        return render(request, 'jobs/job_list_empresa.html', context)

    else:  # Profesional
        profesional = user.profesional

        # Ofertas destacadas (primeras 5)
        ofertas_destacadas = OfertaEmpleo.objects.filter(
            activa=True,
            destacada=True
        ).select_related('empresa__user').annotate(
            postulaciones_count=Count('postulaciones')
        )[:5]

        # Ofertas recomendadas (excluyendo las destacadas y las que ya no están activas)
        ofertas_recomendadas = OfertaEmpleo.objects.filter(
            activa=True
        ).exclude(
            id__in=ofertas_destacadas.values_list('id', flat=True)
        ).select_related('empresa__user').annotate(
            postulaciones_count=Count('postulaciones')
        ).order_by('-fecha_publicacion')[:20]

        # Ofertas guardadas por el profesional
        empleos_guardados_qs = EmpleoGuardado.objects.filter(
            profesional=profesional
        ).select_related('oferta__empresa__user')

        # IDs de ofertas guardadas (para marcar en el template)
        empleos_guardados_ids = list(
            empleos_guardados_qs.values_list('oferta_id', flat=True)
        )

        # Postulaciones activas del profesional
        postulaciones_activas = Postulacion.objects.filter(
            profesional=profesional,
            estado__in=['en_revision', 'entrevista']
        ).select_related('oferta__empresa__user')

        context = {
            'ofertas_destacadas': ofertas_destacadas,
            'ofertas_recomendadas': ofertas_recomendadas,
            'ofertas_guardadas': empleos_guardados_qs,          # Queryset de EmpleoGuardado
            'postulaciones_activas': postulaciones_activas,
            'empleos_guardados_ids': empleos_guardados_ids,
            'user_type': 'profesional',
        }
        return render(request, 'jobs/job_list_profesional.html', context)