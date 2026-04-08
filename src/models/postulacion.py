from django.db import models
from django.utils.translation import gettext_lazy as _
from .profesional import Profesional
from .oferta_empleo import OfertaEmpleo

class Postulacion(models.Model):
    """
    Modelo de Postulación a una oferta de empleo
    """
    ESTADO_CHOICES = [
        ('pendiente', _('Pendiente')),
        ('en_revision', _('En revisión')),
        ('entrevista', _('En entrevista')),
        ('aceptada', _('Aceptada')),
        ('rechazada', _('Rechazada')),
        ('retirada', _('Retirada')),
    ]
    
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        verbose_name=_("Profesional")
    )
    
    oferta = models.ForeignKey(
        OfertaEmpleo,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        verbose_name=_("Oferta")
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name=_("Estado")
    )
    
    # Datos de la aplicación
    habilidades_tecnicas = models.TextField(
        verbose_name=_("Habilidades técnicas"),
        help_text=_("Lista de habilidades separadas por comas")
    )
    @property
    def habilidades_list(self):
        """Retorna las habilidades como lista"""
        if self.habilidades_tecnicas:
            return [h.strip() for h in self.habilidades_tecnicas.split(',') if h.strip()]
        return []
    
    anos_experiencia = models.PositiveIntegerField(
        verbose_name=_("Años de experiencia")
    )
    
    nivel_habilidad = models.CharField(
        max_length=20,
        choices=[
            ('junior', _('Junior')),
            ('mid', _('Mid-level')),
            ('senior', _('Senior')),
        ],
        verbose_name=_("Nivel de habilidad")
    )
    
    telefono_contacto = models.CharField(
        max_length=20,
        verbose_name=_("Teléfono de contacto")
    )
    
    email_contacto = models.EmailField(
        verbose_name=_("Email de contacto")
    )
    
    curriculum = models.FileField(
        upload_to='postulaciones/cvs/',
        verbose_name=_("Currículum")
    )
    
    carta_presentacion = models.TextField(
        blank=True,
        verbose_name=_("Carta de presentación")
    )
    
    fecha_postulacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de postulación")
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última actualización")
    )
    
    guardada = models.BooleanField(
        default=False,
        verbose_name=_("Oferta guardada")
    )
    
    class Meta:
        verbose_name = _("Postulación")
        verbose_name_plural = _("Postulaciones")
        ordering = ['-fecha_postulacion']
        unique_together = ['profesional', 'oferta']
    
    def __str__(self):
        return f"{self.profesional.user.get_full_name()} - {self.oferta.titulo}"