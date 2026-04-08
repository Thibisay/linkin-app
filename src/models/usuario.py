from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    """
    Modelo extendido de Usuario basado en el diagrama de dominio.
    Campos heredados: username, password, email, first_name, last_name
    """
    
    # Campos adicionales del modelo de dominio
    foto = models.ImageField(
        upload_to='usuarios/avatars/',
        null=True,
        blank=True,
        verbose_name=_("Foto de perfil")
    )
    
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Ubicación")
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de registro")
    )
    
    # Tipo de usuario (para diferenciar Profesional vs Empresa)
    TIPO_CHOICES = [
        ('profesional', _('Profesional')),
        ('empresa', _('Empresa')),
    ]
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Tipo de usuario")
    )
    
    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    #def get_avatar_url(self):
        if self.foto:
            return self.foto.url
        # Placeholder por defecto
        return '/static/img/placeholder-avatar.png'
    
    def get_avatar_url(self):
        """Retorna la URL del avatar del usuario"""
        if self.foto:
            return self.foto.url

        # Generar avatar con UI Avatars
        nombre = self.get_full_name() or self.username or 'U'
        # Usar solo las iniciales
        iniciales = ''.join([word[0].upper() for word in nombre.split()[:2]])
        
        # URL de UI Avatars con los colores de Linking X
        return f"https://ui-avatars.com/api/?name={iniciales}&size=128&background=0A66C2&color=fff&bold=true&rounded=true"
    