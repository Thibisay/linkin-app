from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, escape
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.db.models import Count
from .models import (
    Usuario, Profesional, Empresa, 
    Publicacion, Comentario, Like, Seguidor,
    OfertaEmpleo, Postulacion,
    Conversacion, Mensaje
)
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

# ===== CONFIGURACIÓN GENERAL DEL ADMIN =====
admin.site.site_header = _("Linking X - Panel Administrativo")
admin.site.site_title = _("Linking X Admin")
admin.site.index_title = _("Gestión de la Plataforma")

# ===== USUARIO ADMIN =====
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_active', 'fecha_registro']
    list_filter = ['tipo_usuario', 'is_active', 'is_staff', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-fecha_registro']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Información Adicional'), {
            'fields': ('tipo_usuario', 'foto', 'ubicacion', 'fecha_registro')
        }),
    )
    
    readonly_fields = ['fecha_registro']
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuarios activados.', messages.SUCCESS)
    activate_users.short_description = _("Activar usuarios seleccionados")
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuarios desactivados.', messages.WARNING)
    deactivate_users.short_description = _("Desactivar usuarios seleccionados")

# ===== PUBLICACIÓN ADMIN =====
@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'autor_nombre', 'contenido_corto', 'fecha_creacion', 'estado_activo', 'num_likes', 'num_comentarios']
    list_filter = ['is_active', 'fecha_creacion']
    search_fields = ['autor__username', 'autor__email', 'contenido']
    readonly_fields = ['fecha_creacion', 'bloqueado_por', 'fecha_bloqueo']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        (_('Información de la Publicación'), {
            'fields': ('autor', 'contenido', 'imagen', 'video', 'fecha_creacion')
        }),
        (_('Estado de Moderación'), {
            'fields': ('is_active', 'bloqueado_por', 'fecha_bloqueo', 'razon_bloqueo'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['bloquear_publicaciones', 'desbloquear_publicaciones']
    
    def get_queryset(self, request):
        """Usar all_objects para ver todas las publicaciones"""
        qs = Publicacion.all_objects.select_related('autor')
        return qs.annotate(
            _num_likes=Count('likes', distinct=True),
            _num_comentarios=Count('comentarios', distinct=True)
        )
    
    def autor_nombre(self, obj):
        """Nombre del autor - SIN format_html para evitar errores"""
        try:
            if obj and obj.autor:
                return obj.autor.get_full_name() or obj.autor.username
        except:
            pass
        return '-'
    autor_nombre.short_description = _("Autor")
    
    def contenido_corto(self, obj):
        """Preview del contenido"""
        try:
            if obj and obj.contenido:
                return obj.contenido[:100] + ('...' if len(obj.contenido) > 100 else '')
        except:
            pass
        return '-'
    contenido_corto.short_description = _("Contenido")
    
    def estado_activo(self, obj):
        """Estado como texto simple"""
        try:
            if obj:
                return "✓ Activa" if obj.is_active else "✗ Bloqueada"
        except:
            pass
        return '-'
    estado_activo.short_description = _("Estado")
    
    def num_likes(self, obj):
        """Número de likes"""
        try:
            if obj and hasattr(obj, '_num_likes'):
                return obj._num_likes
            elif obj:
                return obj.likes.count()
        except:
            pass
        return 0
    num_likes.short_description = _("Likes")
    
    def num_comentarios(self, obj):
        """Número de comentarios"""
        try:
            if obj and hasattr(obj, '_num_comentarios'):
                return obj._num_comentarios
            elif obj:
                return obj.comentarios.filter(is_active=True).count()
        except:
            pass
        return 0
    num_comentarios.short_description = _("Comentarios")
    
    def bloquear_publicaciones(self, request, queryset):
        """Bloquear publicaciones seleccionadas"""
        count = 0
        for pub in queryset.filter(is_active=True):
            try:
                pub.bloquear(request.user, razon="Bloqueado desde panel admin")
                count += 1
            except Exception as e:
                self.message_user(request, f'Error bloqueando publicación {pub.id}: {str(e)}', messages.ERROR)
        
        if count > 0:
            self.message_user(request, f'{count} publicación(es) bloqueada(s).', messages.WARNING)
    bloquear_publicaciones.short_description = _("🚫 Bloquear publicaciones")
    
    def desbloquear_publicaciones(self, request, queryset):
        """Desbloquear publicaciones seleccionadas"""
        count = 0
        for pub in queryset.filter(is_active=False):
            try:
                pub.desbloquear()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error desbloqueando publicación {pub.id}: {str(e)}', messages.ERROR)
        
        if count > 0:
            self.message_user(request, f'{count} publicación(es) desbloqueada(s).', messages.SUCCESS)
    desbloquear_publicaciones.short_description = _("✓ Desbloquear publicaciones")

# ===== COMENTARIO ADMIN =====
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'autor_nombre', 'pub_id', 'contenido_corto', 'nivel', 'fecha_creacion', 'estado_activo', 'num_respuestas']
    list_filter = ['is_active', 'nivel', 'fecha_creacion']
    search_fields = ['autor__username', 'contenido']
    readonly_fields = ['fecha_creacion', 'nivel', 'bloqueado_por', 'fecha_bloqueo']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        (_('Información del Comentario'), {
            'fields': ('publicacion', 'autor', 'contenido', 'comentario_padre', 'nivel', 'imagen', 'video', 'fecha_creacion')
        }),
        (_('Estado de Moderación'), {
            'fields': ('is_active', 'bloqueado_por', 'fecha_bloqueo', 'razon_bloqueo'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['bloquear_comentarios', 'desbloquear_comentarios']
    
    def get_queryset(self, request):
        """Usar all_objects para ver todos los comentarios"""
        return Comentario.all_objects.select_related('autor', 'publicacion').annotate(
            _num_respuestas=Count('respuestas', distinct=True)
        )
    
    def autor_nombre(self, obj):
        """Nombre del autor - texto simple"""
        try:
            if obj and obj.autor:
                return obj.autor.get_full_name() or obj.autor.username
        except:
            pass
        return '-'
    autor_nombre.short_description = _("Autor")
    
    def pub_id(self, obj):
        """ID de la publicación"""
        try:
            if obj and obj.publicacion:
                return f"Pub #{obj.publicacion.id}"
        except:
            pass
        return '-'
    pub_id.short_description = _("Publicación")
    
    def contenido_corto(self, obj):
        """Preview del contenido"""
        try:
            if obj:
                if not obj.is_active:
                    return "[Bloqueado]"
                if obj.contenido:
                    return obj.contenido[:80] + ('...' if len(obj.contenido) > 80 else '')
        except:
            pass
        return '-'
    contenido_corto.short_description = _("Contenido")
    
    def estado_activo(self, obj):
        """Estado como texto simple"""
        try:
            if obj:
                return "✓ Activo" if obj.is_active else "✗ Bloqueado"
        except:
            pass
        return '-'
    estado_activo.short_description = _("Estado")
    
    def num_respuestas(self, obj):
        """Número de respuestas"""
        try:
            if obj and hasattr(obj, '_num_respuestas'):
                count = obj._num_respuestas
            elif obj:
                count = obj.respuestas.filter(is_active=True).count()
            else:
                count = 0
            
            return f"↳ {count}" if count > 0 else "-"
        except:
            pass
        return '-'
    num_respuestas.short_description = _("Respuestas")
    
    def bloquear_comentarios(self, request, queryset):
        """Bloquear comentarios seleccionados"""
        count = 0
        for comment in queryset.filter(is_active=True):
            try:
                comment.bloquear(request.user, razon="Bloqueado desde panel admin")
                count += 1
            except Exception as e:
                self.message_user(request, f'Error bloqueando comentario {comment.id}: {str(e)}', messages.ERROR)
        
        if count > 0:
            self.message_user(request, f'{count} comentario(s) bloqueado(s).', messages.WARNING)
    bloquear_comentarios.short_description = _("🚫 Bloquear comentarios")
    
    def desbloquear_comentarios(self, request, queryset):
        """Desbloquear comentarios seleccionados"""
        count = 0
        for comment in queryset.filter(is_active=False):
            try:
                comment.desbloquear()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error desbloqueando comentario {comment.id}: {str(e)}', messages.ERROR)
        
        if count > 0:
            self.message_user(request, f'{count} comentario(s) desbloqueado(s).', messages.SUCCESS)
    desbloquear_comentarios.short_description = _("✓ Desbloquear comentarios")

# ===== OTROS MODELOS (SIMPLIFICADOS) =====
@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'titulo_actual', 'cedula', 'genero']
    search_fields = ['user__username', 'user__email', 'titulo_actual', 'cedula']
    
    def usuario(self, obj):
        try:
            if obj and obj.user:
                return obj.user.username
        except:
            pass
        return '-'
    usuario.short_description = _("Usuario")

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'nombre_empresa', 'sector', 'tamano']
    search_fields = ['user__username', 'nombre_empresa', 'rif']
    
    def usuario(self, obj):
        try:
            if obj and obj.user:
                return obj.user.username
        except:
            pass
        return '-'
    usuario.short_description = _("Usuario")

@admin.register(OfertaEmpleo)
class OfertaEmpleoAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'empresa_nombre', 'ubicacion', 'activa', 'fecha_publicacion']
    list_filter = ['activa', 'nivel', 'tipo_empleo', 'modalidad']
    search_fields = ['titulo', 'empresa__nombre_empresa']
    
    def empresa_nombre(self, obj):
        try:
            if obj and obj.empresa:
                return obj.empresa.nombre_empresa
        except:
            pass
        return '-'
    empresa_nombre.short_description = _("Empresa")

@admin.register(Postulacion)
class PostulacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'profesional_nombre', 'oferta_titulo', 'estado', 'fecha_postulacion']
    list_filter = ['estado', 'fecha_postulacion']
    search_fields = ['profesional__user__username', 'oferta__titulo']
    
    def profesional_nombre(self, obj):
        try:
            if obj and obj.profesional and obj.profesional.user:
                return obj.profesional.user.get_full_name() or obj.profesional.user.username
        except:
            pass
        return '-'
    profesional_nombre.short_description = _("Profesional")
    
    def oferta_titulo(self, obj):
        try:
            if obj and obj.oferta:
                return obj.oferta.titulo
        except:
            pass
        return '-'
    oferta_titulo.short_description = _("Oferta")

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario_nombre', 'publicacion_id', 'fecha_creacion']
    search_fields = ['usuario__username']
    
    def usuario_nombre(self, obj):
        try:
            if obj and obj.usuario:
                return obj.usuario.username
        except:
            pass
        return '-'
    usuario_nombre.short_description = _("Usuario")
    
    def publicacion_id(self, obj):
        try:
            if obj and obj.publicacion:
                return f"#{obj.publicacion.id}"
        except:
            pass
        return '-'
    publicacion_id.short_description = _("Publicación")

@admin.register(Seguidor)
class SeguidorAdmin(admin.ModelAdmin):
    list_display = ['id', 'seguidor_nombre', 'seguido_nombre', 'fecha_seguimiento']
    search_fields = ['seguidor__username', 'seguido__username']
    
    def seguidor_nombre(self, obj):
        try:
            if obj and obj.seguidor:
                return obj.seguidor.username
        except:
            pass
        return '-'
    seguidor_nombre.short_description = _("Seguidor")
    
    def seguido_nombre(self, obj):
        try:
            if obj and obj.seguido:
                return obj.seguido.username
        except:
            pass
        return '-'
    seguido_nombre.short_description = _("Seguido")

    # ===== LOGS DE AUDITORÍA =====
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """
    Exponer los Logs de Auditoría nativos de Django.
    Esto permite a los Superusuarios ver quién bloqueó una publicación o comentario, 
    cumpliendo con el requerimiento de seguridad.
    """
    date_hierarchy = 'action_time'
    list_filter = ['user', 'content_type', 'action_flag']
    search_fields = ['object_repr', 'change_message']
    list_display = [
        'action_time', 'user', 'content_type', 
        'object_link', 'action_flag_', 'change_message'
    ]
    
    # Los logs de auditoría son de solo lectura por seguridad estricta
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

    def action_flag_(self, obj):
        flags = {
            1: "Añadido",
            2: "Modificado",
            3: "Eliminado"
        }
        return flags.get(obj.action_flag, "Desconocido")
    action_flag_.short_description = "Acción"

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = mark_safe('<a href="%s">%s</a>' % (
                reverse(f'admin:{ct.app_label}_{ct.model}_change', args=[obj.object_id]),
                escape(obj.object_repr),
            ))
        return link
    object_link.short_description = "Objeto Afectado"