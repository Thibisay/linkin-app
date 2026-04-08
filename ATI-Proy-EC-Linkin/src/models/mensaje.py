from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario
from .conversacion import Conversacion

class Mensaje(models.Model):
    """
    Modelo de Mensaje
    """
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name=_("Conversación")
    )
    
    emisor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name=_("Emisor")
    )
    
    receptor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos',
        verbose_name=_("Receptor")
    )
    
    contenido = models.TextField(
        verbose_name=_("Contenido del mensaje")
    )
    
    archivo = models.FileField(
        upload_to='mensajes/',
        null=True,
        blank=True,
        verbose_name=_("Archivo adjunto")
    )
    
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de envío")
    )
    
    leido = models.BooleanField(
        default=False,
        verbose_name=_("Leído")
    )
    
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de lectura")
    )
    
    class Meta:
        verbose_name = _("Mensaje")
        verbose_name_plural = _("Mensajes")
        ordering = ['fecha_envio']
    
    def __str__(self):
        return f"{self.emisor.get_full_name()} → {self.receptor.get_full_name()}: {self.contenido[:50]}"
    
    def marcar_como_leido(self):
        """Marca el mensaje como leído"""
        if not self.leido:
            from django.utils import timezone
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leido', 'fecha_lectura'])