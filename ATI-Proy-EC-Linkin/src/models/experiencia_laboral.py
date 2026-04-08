from django.db import models
from django.utils.translation import gettext_lazy as _
from .profesional import Profesional

class ExperienciaLaboral(models.Model):
    """
    Experiencia laboral de un profesional
    """
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='experiencias',
        verbose_name=_("Profesional")
    )
    
    empresa = models.CharField(
        max_length=200,
        verbose_name=_("Empresa")
    )
    
    cargo = models.CharField(
        max_length=200,
        verbose_name=_("Cargo")
    )
    
    tipo_empleo = models.CharField(
        max_length=50,
        choices=[
            ('tiempo_completo', _('Tiempo completo')),
            ('medio_tiempo', _('Medio tiempo')),
            ('freelance', _('Freelance')),
            ('pasantia', _('Pasantía')),
            ('practicas', _('Prácticas')),
        ],
        verbose_name=_("Tipo de empleo")
    )
    
    modalidad = models.CharField(
        max_length=50,
        choices=[
            ('presencial', _('Presencial')),
            ('remoto', _('Remoto')),
            ('hibrido', _('Híbrido')),
        ],
        verbose_name=_("Modalidad")
    )
    
    fecha_inicio = models.DateField(
        verbose_name=_("Fecha de inicio")
    )
    
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de finalización")
    )
    
    trabajo_actual = models.BooleanField(
        default=False,
        verbose_name=_("Trabajo actual")
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_("Descripción de responsabilidades")
    )
    
    class Meta:
        verbose_name = _("Experiencia Laboral")
        verbose_name_plural = _("Experiencias Laborales")
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.cargo} en {self.empresa}"