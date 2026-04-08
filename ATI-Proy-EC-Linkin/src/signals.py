from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import Postulacion, Seguidor, Mensaje, Like, Comentario, Notificacion

# ===== HELPER FUNCTION =====
def crear_notificacion(destinatario, emisor, tipo, titulo, mensaje, url=''):
    """
    Función helper para crear notificaciones
    Verifica que el destinatario esté activo y no bloqueado
    """
    # Verificar que el destinatario esté activo
    if not destinatario.is_active:
        return None
    
    # Verificar que el emisor no esté bloqueado (si existe)
    if emisor and hasattr(destinatario, 'usuarios_bloqueados'):
        # Aquí podrías verificar si el emisor está bloqueado por el destinatario
        # if destinatario.usuarios_bloqueados.filter(id=emisor.id).exists():
        #     return None
        pass
    
    # Crear la notificación
    return Notificacion.objects.create(
        destinatario=destinatario,
        emisor=emisor,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url=url
    )


# ===== SEÑAL: NUEVA POSTULACIÓN =====
@receiver(post_save, sender=Postulacion)
def notificar_nueva_postulacion(sender, instance, created, **kwargs):
    """
    Notifica a la empresa cuando recibe una nueva postulación
    """
    if created:
        empresa_user = instance.oferta.empresa.user
        profesional = instance.profesional.user
        
        titulo = _("Nueva postulación recibida")
        mensaje = _(f"{profesional.get_full_name()} ha aplicado a {instance.oferta.titulo}")
        url = reverse('job_applicants', kwargs={'job_id': instance.oferta.id})
        
        crear_notificacion(
            destinatario=empresa_user,
            emisor=profesional,
            tipo='nueva_postulacion',
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )


# ===== SEÑAL: CAMBIO DE ESTADO EN POSTULACIÓN =====
@receiver(post_save, sender=Postulacion)
def notificar_cambio_estado_postulacion(sender, instance, created, **kwargs):
    """
    Notifica al profesional cuando su postulación cambia de estado
    """
    if not created:  # Solo cuando se actualiza
        profesional_user = instance.profesional.user
        
        if instance.estado == 'aceptada':
            titulo = _("¡Felicitaciones! Tu postulación fue aceptada")
            mensaje = _(f"Tu postulación para {instance.oferta.titulo} en {instance.oferta.empresa.nombre_empresa} ha sido aceptada.")
            tipo = 'postulacion_aceptada'
        elif instance.estado == 'rechazada':
            titulo = _("Actualización de tu postulación")
            mensaje = _(f"Tu postulación para {instance.oferta.titulo} en {instance.oferta.empresa.nombre_empresa} no fue seleccionada esta vez.")
            tipo = 'postulacion_rechazada'
        else:
            # Para otros estados (en_revision, entrevista), no notificar
            return
        
        url = reverse('job_detail', kwargs={'job_id': instance.oferta.id})
        
        crear_notificacion(
            destinatario=profesional_user,
            emisor=instance.oferta.empresa.user,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )


# ===== SEÑAL: NUEVO SEGUIDOR =====
@receiver(post_save, sender=Seguidor)
def notificar_nuevo_seguidor(sender, instance, created, **kwargs):
    """
    Notifica al usuario cuando alguien lo sigue
    """
    if created:
        seguido = instance.seguido
        seguidor = instance.seguidor
        
        titulo = _("Nuevo seguidor")
        mensaje = _(f"{seguidor.get_full_name()} ha comenzado a seguirte")
        url = reverse('profile_detail', kwargs={'user_id': seguidor.id})
        
        crear_notificacion(
            destinatario=seguido,
            emisor=seguidor,
            tipo='nuevo_seguidor',
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )


# ===== SEÑAL: NUEVO MENSAJE =====
@receiver(post_save, sender=Mensaje)
def notificar_nuevo_mensaje(sender, instance, created, **kwargs):
    """
    Notifica al receptor cuando recibe un nuevo mensaje
    """
    if created:
        receptor = instance.receptor
        emisor = instance.emisor
        
        titulo = _("Nuevo mensaje")
        mensaje = _(f"{emisor.get_full_name()}: {instance.contenido[:50]}...")
        url = reverse('message_detail', kwargs={'conversacion_id': instance.conversacion.id})
        
        crear_notificacion(
            destinatario=receptor,
            emisor=emisor,
            tipo='nuevo_mensaje',
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )


# ===== SEÑAL: LIKE EN PUBLICACIÓN =====
@receiver(post_save, sender=Like)
def notificar_like_publicacion(sender, instance, created, **kwargs):
    """
    Notifica al autor cuando alguien da like a su publicación
    """
    if created:
        autor = instance.publicacion.autor
        usuario = instance.usuario
        
        # No notificar si el usuario le da like a su propia publicación
        if autor == usuario:
            return
        
        titulo = _("Le gustó tu publicación")
        mensaje = _(f"A {usuario.get_full_name()} le gustó tu publicación")
        url = reverse('feed_home')  # O URL específica de la publicación
        
        crear_notificacion(
            destinatario=autor,
            emisor=usuario,
            tipo='like_publicacion',
            titulo=titulo,
            mensaje=mensaje,
            url=url
        )


# ===== SEÑAL: COMENTARIO EN PUBLICACIÓN =====
@receiver(post_save, sender=Comentario)
def notificar_comentario_publicacion(sender, instance, created, **kwargs):
    """
    Notifica al autor cuando alguien comenta en su publicación
    O cuando alguien responde a su comentario
    """
    if created:
        autor_publicacion = instance.publicacion.autor
        autor_comentario = instance.autor
        
        # Si es una respuesta a un comentario
        if instance.comentario_padre:
            autor_comentario_padre = instance.comentario_padre.autor
            
            # No notificar si el usuario se responde a sí mismo
            if autor_comentario_padre == autor_comentario:
                return
            
            titulo = _("Nueva respuesta a tu comentario")
            mensaje = _(f"{autor_comentario.get_full_name()} respondió a tu comentario: {instance.contenido[:50]}...")
            tipo = 'respuesta_comentario'
            
            crear_notificacion(
                destinatario=autor_comentario_padre,
                emisor=autor_comentario,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                url=reverse('feed_home')
            )
        else:
            # Comentario nuevo en la publicación
            # No notificar si el autor comenta en su propia publicación
            if autor_publicacion == autor_comentario:
                return
            
            titulo = _("Nuevo comentario en tu publicación")
            mensaje = _(f"{autor_comentario.get_full_name()} comentó: {instance.contenido[:50]}...")
            tipo = 'comentario_publicacion'
            
            crear_notificacion(
                destinatario=autor_publicacion,
                emisor=autor_comentario,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                url=reverse('feed_home')
            )