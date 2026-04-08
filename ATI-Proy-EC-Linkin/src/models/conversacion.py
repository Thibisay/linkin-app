from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario
from django.utils import timezone

class Conversacion(models.Model):
    """
    Modelo de Conversación entre dos usuarios
    """
    ESTADO_CHOICES = [
        ('pendiente', _('Pendiente')),
        ('aceptada', _('Aceptada')),
        ('rechazada', _('Rechazada')),
        ('bloqueada', _('Bloqueada')),
    ]
    
    participante_1 = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='conversaciones_iniciadas',
        verbose_name=_("Participante 1")
    )
    
    participante_2 = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='conversaciones_recibidas',
        verbose_name=_("Participante 2")
    )
    
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de inicio")
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última actualización")
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name=_("Estado")
    )
    
    bloqueado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversaciones_bloqueadas',
        verbose_name=_("Bloqueado por")
    )
    
    class Meta:
        verbose_name = _("Conversación")
        verbose_name_plural = _("Conversaciones")
        ordering = ['-fecha_actualizacion']
        unique_together = [
            ['participante_1', 'participante_2']
        ]
    
    def __str__(self):
        return f"{self.participante_1.get_full_name()} ↔ {self.participante_2.get_full_name()}"
    
    def get_otro_participante(self, usuario):
        """Retorna el otro participante de la conversación"""
        if self.participante_1 == usuario:
            return self.participante_2
        return self.participante_1
    
    def get_ultimo_mensaje(self):
        """Retorna el último mensaje de la conversación"""
        return self.mensajes.order_by('-fecha_envio').first()
    
    def mensajes_no_leidos(self, usuario):
        """Retorna la cantidad de mensajes no leídos para el usuario"""
        return self.mensajes.filter(receptor=usuario, leido=False).count()
    
    def esta_bloqueada_por(self, usuario):
        """Verifica si la conversación está bloqueada por el usuario"""
        return self.estado == 'bloqueada' and self.bloqueado_por == usuario
    
    def puede_enviar_mensaje(self, usuario):
        """Verifica si el usuario puede enviar mensajes"""
        if self.estado == 'bloqueada':
            return False
        if self.estado == 'aceptada':
            return True
        # Si está pendiente, solo el iniciador puede enviar el primer mensaje
        return self.participante_1 == usuario