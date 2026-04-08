from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario

class PublicacionManager(models.Manager):
    """Manager para publicaciones activas"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Publicacion(models.Model):
    """
    Modelo de Publicación con soporte para soft delete
    """
    
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='publicaciones',
        verbose_name=_("Autor")
    )
    
    contenido = models.TextField(
        blank=True,
        verbose_name=_("Contenido")
    )
    
    imagen = models.ImageField(
        upload_to='publicaciones/imagenes/',
        null=True,
        blank=True,
        verbose_name=_("Imagen")
    )
    
    video = models.FileField(
        upload_to='publicaciones/videos/',
        null=True,
        blank=True,
        verbose_name=_("Video")
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de publicación")
    )
    
    # ✅ SOFT DELETE
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Activa")
    )
    
    bloqueado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publicaciones_bloqueadas',
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
    objects = PublicacionManager()  # Solo activas
    all_objects = models.Manager()  # Todas (incluyendo bloqueadas)
    
    class Meta:
        verbose_name = _("Publicación")
        verbose_name_plural = _("Publicaciones")
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.autor.get_full_name()} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
    
    def bloquear(self, admin_user, razon=""):
        """Bloquear publicación (soft delete)"""
        from django.utils import timezone
        self.is_active = False
        self.bloqueado_por = admin_user
        self.fecha_bloqueo = timezone.now()
        self.razon_bloqueo = razon
        self.save()
    
    def desbloquear(self):
        """Desbloquear publicación"""
        self.is_active = True
        self.bloqueado_por = None
        self.fecha_bloqueo = None
        self.razon_bloqueo = ""
        self.save()
    
    # === NUEVAS PROPIEDADES PARA EL TEMPLATE ===
    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_comentarios(self):
        return self.comentarios.count()