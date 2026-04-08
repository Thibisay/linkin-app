from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario

class NotificacionManager(models.Manager):
    """Manager para notificaciones activas"""
    def get_queryset(self):
        return super().get_queryset().filter(activa=True)

class Notificacion(models.Model):
    """
    Modelo de Notificación
    """
    TIPO_CHOICES = [
        ('nueva_postulacion', _('Nueva postulación')),
        ('postulacion_aceptada', _('Postulación aceptada')),
        ('postulacion_rechazada', _('Postulación rechazada')),
        ('nuevo_seguidor', _('Nuevo seguidor')),
        ('nuevo_mensaje', _('Nuevo mensaje')),
        ('like_publicacion', _('Like en publicación')),
        ('comentario_publicacion', _('Comentario en publicación')),
        ('respuesta_comentario', _('Respuesta a comentario')),
    ]
    
    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name=_("Destinatario")
    )
    
    emisor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones_enviadas',
        verbose_name=_("Emisor"),
        null=True,
        blank=True
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name=_("Tipo de notificación")
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_("Título")
    )
    
    mensaje = models.TextField(
        verbose_name=_("Mensaje")
    )
    
    url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("URL de destino")
    )
    
    leida = models.BooleanField(
        default=False,
        verbose_name=_("Leída")
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de lectura")
    )
    
    # Para soft delete
    activa = models.BooleanField(
        default=True,
        verbose_name=_("Activa")
    )
    
    # Managers
    objects = NotificacionManager()  # Solo activas
    all_objects = models.Manager()  # Todas
    
    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones")
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['destinatario', 'leida', 'activa']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.tipo} para {self.destinatario.get_full_name()}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            from django.utils import timezone
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])