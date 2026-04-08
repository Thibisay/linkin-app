from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario
from .publicacion import Publicacion

class ComentarioManager(models.Manager):
    """Manager para comentarios activos"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Comentario(models.Model):
    """
    Modelo de Comentario con soporte para soft delete y multimedia
    """
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name=_("Publicación")
    )
    
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name=_("Autor")
    )
    
    contenido = models.TextField(
        verbose_name=_("Contenido")
    )
    
    imagen = models.ImageField(
        upload_to='comentarios/imagenes/',
        null=True,
        blank=True,
        verbose_name=_("Imagen")
    )
    
    video = models.FileField(
        upload_to='comentarios/videos/',
        null=True,
        blank=True,
        verbose_name=_("Video")
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    
    comentario_padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name=_("Comentario padre")
    )
    
    nivel = models.IntegerField(
        default=0,
        verbose_name=_("Nivel de anidación")
    )
    
    # ✅ SOFT DELETE
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Activo")
    )
    
    bloqueado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comentarios_bloqueados',
        verbose_name=_("Bloqueado por")
    )
    
    fecha_bloqueo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de bloqueo")
    )
    
    razon_bloqueo = models.TextField(
        blank=True,
        verbose_name=_("Razón del bloqueo")
    )
    
    # Managers
    objects = ComentarioManager()  # Solo activos
    all_objects = models.Manager()  # Todos (incluyendo bloqueados)
    
    class Meta:
        verbose_name = _("Comentario")
        verbose_name_plural = _("Comentarios")
        ordering = ['fecha_creacion']
    
    def __str__(self):
        return f"Comentario de {self.autor.get_full_name()} en {self.publicacion}"
    
    def save(self, *args, **kwargs):
        """Calcular el nivel de anidación automáticamente"""
        if self.comentario_padre:
            self.nivel = self.comentario_padre.nivel + 1
        else:
            self.nivel = 0
        super().save(*args, **kwargs)
    
    def get_nivel_visual(self):
        """Retorna el nivel visual (máximo 3 para UI)"""
        return min(self.nivel, 3)
    
    def get_respuestas(self):
        """Retorna las respuestas directas a este comentario"""
        return self.respuestas.filter(is_active=True)
    
    def total_respuestas(self):
        """Cuenta todas las respuestas recursivamente"""
        total = self.respuestas.filter(is_active=True).count()
        for respuesta in self.respuestas.filter(is_active=True):
            total += respuesta.total_respuestas()
        return total
    
    def bloquear(self, admin_user, razon=""):
        """Bloquear comentario (soft delete)"""
        from django.utils import timezone
        self.is_active = False
        self.bloqueado_por = admin_user
        self.fecha_bloqueo = timezone.now()
        self.razon_bloqueo = razon
        self.save()
    
    def desbloquear(self):
        """Desbloquear comentario"""
        self.is_active = True
        self.bloqueado_por = None
        self.fecha_bloqueo = None
        self.razon_bloqueo = ""
        self.save()
    
    def get_contenido_display(self):
        """Retorna el contenido o mensaje de bloqueado"""
        if not self.is_active:
            return _("[Comentario bloqueado por el Administrador]")
        return self.contenido