# src/models/empleo_guardado.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .profesional import Profesional
from .oferta_empleo import OfertaEmpleo


class EmpleoGuardado(models.Model):
    """
    Modelo para empleos guardados por profesionales
    SEPARADO de Postulacion - solo para guardar favoritos
    """
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='empleos_guardados',
        verbose_name=_("Profesional")
    )
    
    oferta = models.ForeignKey(
        OfertaEmpleo,
        on_delete=models.CASCADE,
        related_name='guardado_por',
        verbose_name=_("Oferta de empleo")
    )
    
    fecha_guardado = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de guardado")
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name=_("Notas personales")
    )
    
    class Meta:
        verbose_name = _("Empleo guardado")
        verbose_name_plural = _("Empleos guardados")
        unique_together = ['profesional', 'oferta']
        ordering = ['-fecha_guardado']
        indexes = [
            models.Index(fields=['profesional', '-fecha_guardado']),
        ]
    
    def __str__(self):
        return f"{self.profesional.user.get_full_name()} - {self.oferta.titulo}"