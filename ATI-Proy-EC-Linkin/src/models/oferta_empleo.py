from django.db import models
from django.utils.translation import gettext_lazy as _
from .empresa import Empresa
from .usuario import Usuario

class OfertaEmpleo(models.Model):
    """
    Modelo de Oferta de Empleo
    """
    MODALIDAD_CHOICES = [
        ('presencial', _('Presencial')),
        ('remoto', _('Remoto')),
        ('hibrido', _('Híbrido')),
    ]
    
    TIPO_EMPLEO_CHOICES = [
        ('tiempo_completo', _('Tiempo completo')),
        ('medio_tiempo', _('Medio tiempo')),
        ('freelance', _('Freelance')),
        ('pasantia', _('Pasantía')),
        ('temporal', _('Temporal')),
    ]
    
    NIVEL_CHOICES = [
        ('junior', _('Junior')),
        ('mid', _('Mid-level')),
        ('senior', _('Senior')),
        ('lead', _('Lead')),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='ofertas',
        verbose_name=_("Empresa")
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_("Título del puesto")
    )
    
    descripcion = models.TextField(
        verbose_name=_("Descripción del puesto")
    )
    
    requisitos = models.TextField(
        verbose_name=_("Requisitos"),
        help_text=_("Habilidades y experiencia requerida")
    )
    
    responsabilidades = models.TextField(
        blank=True,
        verbose_name=_("Responsabilidades")
    )
    
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        verbose_name=_("Nivel de experiencia")
    )
    
    tipo_empleo = models.CharField(
        max_length=20,
        choices=TIPO_EMPLEO_CHOICES,
        verbose_name=_("Tipo de empleo")
    )
    
    modalidad = models.CharField(
        max_length=20,
        choices=MODALIDAD_CHOICES,
        verbose_name=_("Modalidad")
    )
    
    ubicacion = models.CharField(
        max_length=200,
        verbose_name=_("Ubicación")
    )
    
    salario_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Salario mínimo")
    )
    
    salario_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Salario máximo")
    )
    
    mostrar_salario = models.BooleanField(
        default=True,
        verbose_name=_("Mostrar salario públicamente")
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_("Oferta activa")
    )
    
    destacada = models.BooleanField(
        default=False,
        verbose_name=_("Oferta destacada")
    )
    
    fecha_publicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de publicación")
    )
    
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de cierre")
    )
    
    vistas = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Cantidad de vistas")
    )
    
    class Meta:
        verbose_name = _("Oferta de Empleo")
        verbose_name_plural = _("Ofertas de Empleo")
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre_empresa}"
    
    def get_rango_salario(self):
        """Retorna el rango salarial formateado"""
        if not self.mostrar_salario:
            return _("No especificado")
        if self.salario_min and self.salario_max:
            return f"${self.salario_min:,.0f} - ${self.salario_max:,.0f}"
        elif self.salario_min:
            return f"Desde ${self.salario_min:,.0f}"
        return _("A convenir")