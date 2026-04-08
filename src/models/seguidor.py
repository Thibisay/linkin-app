from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario

class Seguidor(models.Model):
    """
    Modelo para el sistema de seguidores
    """
    seguidor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='siguiendo',
        verbose_name=_("Seguidor")
    )
    
    seguido = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='seguidores',
        verbose_name=_("Seguido")
    )
    
    fecha_seguimiento = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de seguimiento")
    )
    
    class Meta:
        verbose_name = _("Seguidor")
        verbose_name_plural = _("Seguidores")
        unique_together = ['seguidor', 'seguido']
        ordering = ['-fecha_seguimiento']
    
    def __str__(self):
        return f"{self.seguidor.get_full_name()} sigue a {self.seguido.get_full_name()}"