from django.test import TestCase, Client
from django.urls import reverse
from src.models import Usuario, Empresa, OfertaEmpleo, Publicacion
from django.core.files.uploadedfile import SimpleUploadedFile

class IdentidadTestCase(TestCase):
    """Pruebas para el Caso de Uso 01: Gestionar Identidad"""
    
    def setUp(self):
        # El setUp se ejecuta antes de cada prueba. 

        # Cliente web simulado.
        self.client = Client()
        
        # Usuario inicial para simular que ese email ya está en uso en la BD
        self.usuario_existente = Usuario.objects.create_user(
            username='existente@gmail.com',
            email='existente@gmail.com',
            password='password123', 
            tipo_usuario='profesional'
        )

    def test_registro_profesional_email_duplicado(self):
        """
        TC 01.1: Verificar que el sistema no permite duplicidad de emails al registrar un usuario nuevo.
        """
        # Intetar registrar un nuevo profesional con el MISMO email
        url = reverse('auth_register_profesional')
        datos_registro = {
            'first_name': 'Juan',
            'last_name': 'Perez',
            'email': 'existente@gmail.com', # <-- Email duplicado
            'cedula': '25123456',
            'fecha_nacimiento': '1995-05-15',
            'genero': 'M',
            'password1': 'NuevaPassword123',
            'password2': 'NuevaPassword123'
        }
        
        # Sumulación de que un usuario llena el formulario y hace clic en Enviar 
        response = self.client.post(url, datos_registro)
        
        # El formulario debe fallar y volver a cargar la página (Status 200)
        self.assertEqual(response.status_code, 200)
        
        # Se extrae el formulario directamente del contexto 
        form = response.context['form']
        
        # Verifica que el formulario NO haya pasado la validación
        self.assertFalse(form.is_valid())
        
        # Comprueba que el formulario tenga errores registrados
        self.assertTrue(form.errors, "El formulario debería tener errores por el email duplicado")
        
        # No se debe crear el registro en la base de datos (sigue habiendo 1 solo usuario)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_registro_empresa_email_duplicado(self):
        """
        TC 01.2: Verificar que el sistema no permite duplicidad de emails al registrar una empresa nueva.
        """
        url = reverse('auth_register_empresa')
        datos_registro = {
            'email': 'existente@gmail.com', # <-- El mismo email que creamos en del setUp
            'nombre_empresa': 'Tech Solutions CA',
            'rif': 'J-987654321',
            'tipo_empresa': 'Corporación',
            'password1': 'NuevaPassword123',
            'password2': 'NuevaPassword123'
        }
        
        response = self.client.post(url, datos_registro)
        
        # El formulario falla y vuelve a cargar (Status 200)
        self.assertEqual(response.status_code, 200)
        
        # Extracción del formulario
        form = response.context['form']
        
        # Verifica que sea inválido y tenga errores
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors, "El formulario debería rechazar a la empresa por email duplicado")
        
        # Verifica que que en la base de datos no creó el usuario intruso
        self.assertEqual(Usuario.objects.count(), 1)


class OfertaEmpleoTestCase(TestCase):
    """Pruebas para el Caso de Uso 07: Publicar Vacante"""

    def setUp(self):
        self.client = Client()
        
        # Creación de Empresa Logueada para publicar ofertas
        self.usuario_empresa = Usuario.objects.create_user(
            username='empresa@test.com',
            email='empresa@test.com',
            password='PasswordEmpresa123',
            tipo_usuario='empresa'
        )
        self.empresa = Empresa.objects.create(
            user=self.usuario_empresa,
            nombre_empresa='Tech CA',
            rif='J-123456789',
            tipo_empresa='Corporación'
        )
        
        # Inicio de sesión para simular que la empresa está logueada
        self.client.login(username='empresa@test.com', password='PasswordEmpresa123')

    def test_crear_oferta_datos_invalidos(self):
        """
        TC 07.1: Verificar la integridad de los datos antes de almacenar. Si encuentra un dato inválido, cancela la creación.
        """
        url = reverse('create_job')
        
        # Se envía un formulario POST vacío intencionalmente para forzar errores de validación
        datos_invalidos = {}
        
        response = self.client.post(url, datos_invalidos)
        
        # Verifica los resultados esperados:

        # El servidor devuelve el formulario con errores (Status 200)
        self.assertEqual(response.status_code, 200)
        
        # Verifica que el formulario tiene errores en campos requeridos
        self.assertTrue(response.context['form'].errors)
        
        # Se cancela la creación (No hay ofertas en la BD)
        self.assertEqual(OfertaEmpleo.objects.count(), 0)


class PublicacionTestCase(TestCase):
    """Pruebas para el Caso de Uso 05: Hacer Publicaciones"""

    def setUp(self):
        self.client = Client()
        
        # Crear un usuario logueado para poder publicar
        self.usuario = Usuario.objects.create_user(
            username='creador@test.com',
            email='creador@test.com',
            password='Password123',
            tipo_usuario='profesional'
        )
        self.client.login(username='creador@test.com', password='Password123')

    def test_crear_post_multimedia_limite_excedido(self):
        """
        TC 05.1: Archivo > 10MB -> Mostrar error de límite excedido. El sistema debe interrumpir la carga y no guardar la publicación.
        """
        url = reverse('crear_publicacion')
        
        # Simular un archivo de video de 11 MB (11 * 1024 * 1024 bytes)

        # Llena el archivo con ceros binarios para que alcance el peso
        dummy_data = b'0' * (11 * 1024 * 1024)
        
        video_pesado = SimpleUploadedFile(
            name="video_gigante.mp4",
            content=dummy_data,              # Agrega los 11MB de peso
            content_type="video/mp4"         # Le dice a Django que "finja" que es un video
        )

        datos_post = {
            'contenido': '¡Miren este video super largo en 4K!',
            'video': video_pesado
        }
        
        # Enviar la petición POST
        response = self.client.post(url, datos_post)
        
        # Comprobación de que el sistema no creó la publicación en la BD
        self.assertEqual(Publicacion.objects.count(), 0, "No debería crearse el post porque el archivo pesa 11MB")
        
        # Comprueba que la vista redirigió de vuelta al feed (código 302 Found)
        self.assertEqual(response.status_code, 302)


class ModeracionTestCase(TestCase):
    """Pruebas para el Caso de Uso 12: Moderación de Contenidos"""

    def setUp(self):
        self.client = Client()
        
        # Usuario normal (autor de la publicación)
        self.autor = Usuario.objects.create_user(
            username='autor@test.com',
            email='autor@test.com',
            password='Password123',
            tipo_usuario='profesional'
        )

        # Usuario administrador (moderador)
        self.admin = Usuario.objects.create_superuser(
            username='admin@test.com',
            email='admin@test.com',
            password='AdminPassword123'
        )

        # Se crea una publicación normal antes de iniciar la prueba
        self.publicacion = Publicacion.objects.create(
            autor=self.autor,
            contenido='Esta es una publicación de prueba que será bloqueada.',
        )

    def test_bloqueo_publicacion_oculta_feed(self):
        """
        TC 12.1: Asegurar que un post bloqueado no sea accesible. Verifica que el Soft Delete funciona y la oculta del feed público.
        """
        # Se verifica que inicialmente la publicación está activa y visible
        self.assertTrue(self.publicacion.is_active)
        self.assertEqual(Publicacion.objects.count(), 1, "La publicación debería ser visible inicialmente")

        # El administrador bloquea el post
        self.publicacion.bloquear(admin_user=self.admin, razon='Contenido inapropiado')

        # Verifica que el estado interno cambió correctamente
        self.assertFalse(self.publicacion.is_active)
        self.assertEqual(self.publicacion.bloqueado_por, self.admin)

        # Verificaa que la publicación ya no aparece en el conteo normal de publicaciones activas
        self.assertEqual(
            Publicacion.objects.count(), 
            0, 
            "La publicación bloqueada no debe aparecer en el conteo normal"
        )

        # Verifica que no se borró de verdad (Soft Delete exitoso)
        self.assertEqual(
            Publicacion.all_objects.count(), 
            1, 
            "La publicación no debe borrarse de la BD, solo ocultarse"
        )

        # Prueba de integración con la Vista:

        # Inicio de sesión como un usuario normal e ingresa al feed
        self.client.login(username='autor@test.com', password='Password123')
        url_feed = reverse('feed_home')
        response = self.client.get(url_feed)

        # El feed carga con éxito (código 200)
        self.assertEqual(response.status_code, 200)
        
        # Pero la lista de publicaciones enviada al HTML debe estar vacía
        self.assertEqual(
            len(response.context['publicaciones']), 
            0, 
            "El feed no debe mostrar publicaciones bloqueadas"
        )