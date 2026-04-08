import django_filters
from django.db.models import Q, Count, Sum, F, ExpressionWrapper, IntegerField
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone

from src.models import OfertaEmpleo, Profesional, Usuario


class OfertaEmpleoFilter(django_filters.FilterSet):
    """
    Filtro avanzado para búsqueda de empleos
    Compatible con Django 6 y django-filter 24+
    """
    # Búsqueda general
    q = django_filters.CharFilter(
        method='search_query',
        label=_('Búsqueda')
    )
    
    # Ubicación
    ubicacion = django_filters.CharFilter(
        field_name='ubicacion',
        lookup_expr='icontains',
        label=_('Ubicación')
    )
    
    # Tipo de empleo
    tipo_empleo = django_filters.ChoiceFilter(
        field_name='tipo_empleo',
        choices=OfertaEmpleo.TIPO_EMPLEO_CHOICES,
        label=_('Tipo de empleo')
    )
    
    # Modalidad
    modalidad = django_filters.ChoiceFilter(
        field_name='modalidad',
        choices=OfertaEmpleo.MODALIDAD_CHOICES,
        label=_('Modalidad')
    )
    
    # Nivel
    nivel = django_filters.ChoiceFilter(
        field_name='nivel',
        choices=OfertaEmpleo.NIVEL_CHOICES,
        label=_('Nivel')
    )
    
    # Salario mínimo
    salario_min = django_filters.NumberFilter(
        field_name='salario_min',
        lookup_expr='gte',
        label=_('Salario mínimo')
    )
    
    # Salario máximo
    salario_max = django_filters.NumberFilter(
        field_name='salario_max',
        lookup_expr='lte',
        label=_('Salario máximo')
    )
    
    # Publicado recientemente (últimos N días)
    dias_publicacion = django_filters.NumberFilter(
        method='filter_recent',
        label=_('Días desde publicación')
    )
    
    class Meta:
        model = OfertaEmpleo
        fields = ['ubicacion', 'tipo_empleo', 'modalidad', 'nivel']
    
    def search_query(self, queryset, name, value):
        """Búsqueda por título, descripción, requisitos o responsabilidades"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(titulo__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(requisitos__icontains=value) |
            Q(responsabilidades__icontains=value) |
            Q(empresa__nombre_empresa__icontains=value)
        )
    
    def filter_recent(self, queryset, name, value):
        """Filtrar por empleos publicados en los últimos N días"""
        if not value:
            return queryset
        
        fecha_limite = timezone.now() - timedelta(days=int(value))
        return queryset.filter(fecha_publicacion__gte=fecha_limite)


class ProfesionalFilter(django_filters.FilterSet):
    """
    Filtro avanzado para búsqueda de talento
    Compatible con Django 6 y django-filter 24+
    """
    # Búsqueda general
    q = django_filters.CharFilter(
        method='search_query',
        label=_('Búsqueda')
    )
    
    # Habilidad específica
    habilidad = django_filters.CharFilter(
        method='filter_by_habilidad',
        label=_('Habilidad')
    )
    
    # Nivel de habilidad
    nivel_habilidad = django_filters.ChoiceFilter(
        method='filter_by_nivel_habilidad',
        choices=[
            ('basico', _('Básico')),
            ('intermedio', _('Intermedio')),
            ('avanzado', _('Avanzado')),
            ('experto', _('Experto')),
        ],
        label=_('Nivel de habilidad')
    )
    
    # Ubicación
    ubicacion = django_filters.CharFilter(
        field_name='user__ubicacion',
        lookup_expr='icontains',
        label=_('Ubicación')
    )
    
    # Años de experiencia mínimos
    anos_experiencia_min = django_filters.NumberFilter(
        method='filter_by_experience',
        label=_('Años de experiencia mínimos')
    )
    
    # Género
    genero = django_filters.ChoiceFilter(
        field_name='genero',
        choices=[
            ('M', _('Masculino')),
            ('F', _('Femenino')),
            ('O', _('Otro')),
        ],
        label=_('Género')
    )
    
    class Meta:
        model = Profesional
        fields = ['ubicacion', 'genero']
    
    def search_query(self, queryset, name, value):
        """Búsqueda por nombre, título o descripción"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(titulo_actual__icontains=value) |
            Q(descripcion_personal__icontains=value)
        )
    
    def filter_by_habilidad(self, queryset, name, value):
        """Filtrar por habilidad específica"""
        if not value:
            return queryset
        
        return queryset.filter(
            habilidades__nombre__icontains=value
        ).distinct()
    
    def filter_by_nivel_habilidad(self, queryset, name, value):
        """Filtrar por nivel de habilidad"""
        if not value:
            return queryset
        
        return queryset.filter(
            habilidades__nivel=value
        ).distinct()
    
    def filter_by_experience(self, queryset, name, value):
        """
        Filtrar por años de experiencia (calculado desde experiencias)
        Compatible con Django 6
        """
        if not value:
            return queryset
        
        try:
            # Anotar con años de experiencia totales
            queryset = queryset.annotate(
                total_experience=Sum(
                    ExpressionWrapper(
                        F('experiencias__fecha_fin__year') - F('experiencias__fecha_inicio__year'),
                        output_field=IntegerField()
                    )
                )
            )
            return queryset.filter(total_experience__gte=int(value))
        except Exception as e:
            # Si falla, retornar queryset sin filtrar
            return queryset