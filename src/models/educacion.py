from django.db import models
from django.utils.translation import gettext_lazy as _
from .profesional import Profesional

class Educacion(models.Model):
    """
    Educación/Formación académica de un profesional
    """
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='educaciones',
        verbose_name=_("Profesional")
    )
    
    institucion = models.CharField(
        max_length=200,
        verbose_name=_("Institución")
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_("Título/Grado"),
        help_text=_("Ej: Ingeniería en Computación")
    )
    
    campo_estudio = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Campo de estudio")
    )
    
    fecha_inicio = models.DateField(
        verbose_name=_("Fecha de inicio")
    )
    
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de finalización"),
        help_text=_("Dejar en blanco si está en curso")
    )
    
    en_curso = models.BooleanField(
        default=False,
        verbose_name=_("Actualmente cursando")
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_("Descripción")
    )
    
    class Meta:
        verbose_name = _("Educación")
        verbose_name_plural = _("Educación")
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.institucion}"