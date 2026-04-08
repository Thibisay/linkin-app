from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario
from .publicacion import Publicacion

class Like(models.Model):
    """
    Modelo para los likes en publicaciones
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_("Usuario")
    )
    
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_("Publicación")
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    
    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        unique_together = ['usuario', 'publicacion']
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} le dio like a {self.publicacion}"