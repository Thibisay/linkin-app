from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario

class Profesional(models.Model):
    """
    Perfil extendido para usuarios profesionales/estudiantes
    """
    GENERO_CHOICES = [
        ('masculino', _('Masculino')),
        ('femenino', _('Femenino')),
        ('otro', _('Otro')),
        ('prefiero_no_decir', _('Prefiero no decir')),
    ]
    
    user = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='profesional',
        verbose_name=_("Usuario")
    )
    
    # Datos básicos (del registro)
    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Cédula de identidad")
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name=_("Fecha de nacimiento")
    )
    
    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
        default='prefiero_no_decir',
        verbose_name=_("Género")
    )
    
    # Perfil profesional
    descripcion_personal = models.TextField(
        blank=True,
        verbose_name=_("Acerca de mí"),
        help_text=_("Descripción profesional breve")
    )
    
    titulo_actual = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Título/Cargo actual"),
        help_text=_("Ej: Estudiante de Ingeniería en Computación")
    )
    
    # Preferencias personales (opcionales)
    color_favorito = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Color favorito")
    )
    
    libro_favorito = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Libro favorito")
    )
    
    musica_favorita = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Música favorita")
    )
    
    videojuegos_favoritos = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Videojuegos favoritos")
    )
    
    # Enlaces externos
    sitio_web = models.URLField(
        blank=True,
        verbose_name=_("Sitio web personal")
    )
    
    linkedin_url = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn")
    )
    
    github_url = models.URLField(
        blank=True,
        verbose_name=_("GitHub")
    )
    
    twitter_url = models.URLField(
        blank=True,
        verbose_name=_("Twitter/X")
    )
    
    class Meta:
        verbose_name = _("Profesional")
        verbose_name_plural = _("Profesionales")
    
    def __str__(self):
        return f"Profesional: {self.user.get_full_name()}"