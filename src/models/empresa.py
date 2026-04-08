from django.db import models
from django.utils.translation import gettext_lazy as _
from .usuario import Usuario

class Empresa(models.Model):
    """
    Perfil extendido para usuarios empresa
    """
    TIPO_EMPRESA_CHOICES = [
        ('startup', _('Startup')),
        ('pyme', _('PYME')),
        ('corporacion', _('Corporación')),
        ('ong', _('ONG')),
        ('gobierno', _('Gobierno')),
        ('educacion', _('Institución Educativa')),
    ]
    
    TAMANO_CHOICES = [
        ('1-10', _('1-10 empleados')),
        ('11-50', _('11-50 empleados')),
        ('51-200', _('51-200 empleados')),
        ('201-500', _('201-500 empleados')),
        ('501-1000', _('501-1000 empleados')),
        ('1000+', _('Más de 1000 empleados')),
    ]
    
    user = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='empresa',
        verbose_name=_("Usuario")
    )
    
    # Datos básicos (del registro)
    nombre_empresa = models.CharField(
        max_length=200,
        verbose_name=_("Nombre de la empresa")
    )
    
    rif = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("RIF")
    )
    
    tipo_empresa = models.CharField(
        max_length=20,
        choices=TIPO_EMPRESA_CHOICES,
        verbose_name=_("Tipo de empresa")
    )
    
    # Overview
    descripcion_breve = models.TextField(
        blank=True,
        verbose_name=_("Descripción breve"),
        help_text=_("Descripción corta de la empresa")
    )
    
    descripcion_completa = models.TextField(
        blank=True,
        verbose_name=_("Descripción completa"),
        help_text=_("Información detallada sobre la empresa")
    )
    
    sector = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Sector/Industria")
    )
    
    tamano = models.CharField(
        max_length=20,
        choices=TAMANO_CHOICES,
        blank=True,
        verbose_name=_("Tamaño de la empresa")
    )
    
    ano_fundacion = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Año de fundación")
    )
    
    # Contacto
    sitio_web = models.URLField(
        blank=True,
        verbose_name=_("Sitio web")
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Teléfono")
    )
    
    email_contacto = models.EmailField(
        blank=True,
        verbose_name=_("Email de contacto")
    )
    
    # Redes sociales
    linkedin_url = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn")
    )
    
    facebook_url = models.URLField(
        blank=True,
        verbose_name=_("Facebook")
    )
    
    instagram_url = models.URLField(
        blank=True,
        verbose_name=_("Instagram")
    )
    
    class Meta:
        verbose_name = _("Empresa")
        verbose_name_plural = _("Empresas")
    
    def __str__(self):
        return self.nombre_empresa