from django.urls import path

from .views import search
from .views import notifications
from .views import (
    auth_login,
    auth_logout,
    auth_register_role,
    auth_register_profesional,
    auth_register_empresa,
    feed_home,
    profile_detail,
    profile_edit,
    profile_add_skill,
    profile_add_education,
    profile_add_experience,
    job_list,
    job_detail,
    job_apply,
    message_list,
    message_detail,
    add_section,
    job_applicants,
    job_manage,
    jobs,
    feed,
)
from .views import api

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('login/', auth_login.login_view, name='auth_login'),
    path('logout/', auth_logout.logout_view, name='auth_logout'),
    path('register/', auth_register_role.register_role_view, name='auth_register_role'),
    path('register/profesional/', auth_register_profesional.register_profesional_view, name='auth_register_profesional'),
    path('register/empresa/', auth_register_empresa.register_empresa_view, name='auth_register_empresa'),
    
    # ==================== CORE ====================
    path('', feed_home, name='feed_home'),
    
    # ==================== PROFILE ====================
    # Detail & Edit
    path('profile/<int:user_id>/', profile_detail.profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/edit/', profile_edit.profile_edit, name='profile_edit'),
    
    # Skills
    path('profile/<int:user_id>/skills/add/', profile_add_skill.add_skill, name='add_skill'),
    path('profile/<int:user_id>/skills/<int:skill_id>/delete/', profile_add_skill.delete_skill, name='delete_skill'),
    
    # Education
    path('profile/<int:user_id>/education/add/', profile_add_education.add_education, name='add_education'),
    path('profile/<int:user_id>/education/<int:education_id>/edit/', profile_add_education.edit_education, name='edit_education'),
    path('profile/<int:user_id>/education/<int:education_id>/delete/', profile_add_education.delete_education, name='delete_education'),
    
    # Experience
    path('profile/<int:user_id>/experience/add/', profile_add_experience.add_experience, name='add_experience'),
    path('profile/<int:user_id>/experience/<int:experience_id>/edit/', profile_add_experience.edit_experience, name='edit_experience'),
    path('profile/<int:user_id>/experience/<int:experience_id>/delete/', profile_add_experience.delete_experience, name='delete_experience'),
    
    # Section Management
    path('profile/section/add/<str:section_type>/', add_section.add_section, name='add_section'),
    path('profile/section/edit/<str:section_type>/<int:section_id>/', add_section.edit_section, name='edit_section'),
    path('profile/section/delete/<str:section_type>/<int:section_id>/', add_section.delete_section, name='delete_section'),
    
    # ==================== JOBS ====================
    # List & Detail
    path('jobs/', job_list, name='job_list'),
    path('jobs/<int:job_id>/', job_detail.job_detail, name='job_detail'),
    
    # Apply & Save
    path('jobs/<int:job_id>/apply/', job_apply.job_apply, name='job_apply'),
    path('jobs/<int:job_id>/save/', jobs.guardar_empleo, name='guardar_empleo'),
    path('jobs/saved/', jobs.empleos_guardados, name='empleos_guardados'),
    
    # Management (Empresas)
    path('jobs/create/', job_manage.create_job, name='create_job'),
    path('jobs/<int:job_id>/edit/', job_manage.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/toggle-status/', job_manage.toggle_job_status, name='toggle_job_status'),
    path('jobs/<int:job_id>/delete/', job_manage.delete_job, name='delete_job'),
    
    # Applicants (Empresas)
    path('jobs/<int:job_id>/applicants/', job_applicants.job_applicants, name='job_applicants'),
    path('jobs/application/<int:application_id>/update-status/', job_applicants.update_application_status, name='update_application_status'),
    
    # ==================== MESSAGES ====================
    path('messages/', message_list.message_list, name='message_list'),
    path('messages/<int:conversation_id>/', message_detail.message_detail, name='message_detail'),
    path('messages/<int:conversation_id>/send/', message_detail.send_message, name='send_message'),
    path('messages/create/<int:user_id>/', message_detail.create_conversation, name='create_conversation'),
    
    # Message Actions
    path('messages/<int:conversation_id>/accept/', message_detail.accept_conversation, name='accept_conversation'),
    path('messages/<int:conversation_id>/reject/', message_detail.reject_conversation, name='reject_conversation'),
    path('messages/<int:conversation_id>/block/', message_detail.block_conversation, name='block_conversation'),
    path('messages/<int:conversation_id>/unblock/', message_detail.unblock_conversation, name='unblock_conversation'),
    
    # ==================== FEED ====================
    path('feed/post/create/', feed.crear_publicacion, name='crear_publicacion'),
    path('feed/post/<int:publicacion_id>/like/', feed.toggle_like, name='toggle_like'),
    path('feed/post/<int:publicacion_id>/comment/', feed.crear_comentario, name='crear_comentario'),
    path('feed/post/<int:publicacion_id>/comments/', feed.cargar_comentarios, name='cargar_comentarios'),
    path('feed/user/<int:usuario_id>/follow/', feed.toggle_seguir, name='toggle_seguir'),
    
    # ==================== SEARCH ====================
    path('search/', search.search_general, name='search_general'),
    path('search/jobs/', search.search_jobs, name='search_jobs'),
    path('search/talent/', search.search_talent, name='search_talent'),
    path('search/jobs/advanced/', jobs.busqueda_avanzada_empleos, name='busqueda_avanzada_empleos'),
    
    # ==================== NOTIFICATIONS ====================
    path('notifications/', notifications.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', notifications.mark_as_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', notifications.mark_all_as_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', notifications.delete_notification, name='delete_notification'),
    
    # ==================== API ====================
    path('api/search-users/', api.search_users, name='api_search_users'),
    path('api/notifications/count/', notifications.get_notifications_count, name='notifications_count'),
]