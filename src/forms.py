from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Profesional, Empresa, Habilidad, Educacion, ExperienciaLaboral
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import OfertaEmpleo

class OfertaEmpleoForm(forms.ModelForm):
    class Meta:
        model = OfertaEmpleo
        fields = [
            'titulo',
            'descripcion',
            'requisitos',
            'responsabilidades',
            'nivel',
            'tipo_empleo',
            'modalidad',
            'ubicacion',
            'salario_min',
            'salario_max',
            'mostrar_salario',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Desarrollador Full Stack Senior'),
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Describe el puesto, qué buscan y qué ofrecen...'),
            }),
            'requisitos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Lista los requisitos, uno por línea...'),
            }),
            'responsabilidades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe las responsabilidades del puesto...'),
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tipo_empleo': forms.Select(attrs={
                'class': 'form-select',
            }),
            'modalidad': forms.Select(attrs={
                'class': 'form-select',
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Caracas, Venezuela (Remoto)'),
            }),
            'salario_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000',
                'step': '0.01',
            }),
            'salario_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '3000',
                'step': '0.01',
            }),
            'mostrar_salario': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'titulo': _('Título del puesto'),
            'descripcion': _('Descripción'),
            'requisitos': _('Requisitos'),
            'responsabilidades': _('Responsabilidades'),
            'nivel': _('Nivel de experiencia'),
            'tipo_empleo': _('Tipo de empleo'),
            'modalidad': _('Modalidad de trabajo'),
            'ubicacion': _('Ubicación'),
            'salario_min': _('Salario mínimo (USD)'),
            'salario_max': _('Salario máximo (USD)'),
            'mostrar_salario': _('Mostrar salario públicamente'),
        }

# ========== AUTHENTICATION FORMS ==========

class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'ejemplo@linkingx.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )


class ProfesionalRegistrationForm(UserCreationForm):
    """Formulario de registro para profesionales"""
    
    # Campos de Usuario
    first_name = forms.CharField(
        label=_("Nombres"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Juan Carlos')
        })
    )
    
    last_name = forms.CharField(
        label=_("Apellidos"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Pérez García')
        })
    )
    
    email = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'ejemplo@gmail.com'
        })
    )
    
    # Campos de Profesional
    cedula = forms.CharField(
        label=_("Cédula de identidad"),
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '12345678'
        }),
        help_text=_("Solo números, sin puntos ni guiones")
    )
    
    fecha_nacimiento = forms.DateField(
        label=_("Fecha de nacimiento"),
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    
    genero = forms.ChoiceField(
        label=_("Género"),
        choices=Profesional.GENERO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    # Override password fields
    password1 = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        }),
        help_text=_("Mínimo 8 caracteres")
    )
    
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove auto-generated help texts
        self.fields['password1'].help_text = _("Mínimo 8 caracteres")
        self.fields['password2'].help_text = None
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.tipo_usuario = 'profesional'
        
        if commit:
            user.save()
            # Crear perfil de profesional
            Profesional.objects.create(
                user=user,
                cedula=self.cleaned_data['cedula'],
                fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
                genero=self.cleaned_data['genero']
            )
        
        return user


class EmpresaRegistrationForm(UserCreationForm):
    """Formulario de registro para empresas"""
    
    email = forms.EmailField(
        label=_("Correo electrónico corporativo"),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'contacto@empresa.com'
        })
    )
    
    # Campos específicos de Empresa
    nombre_empresa = forms.CharField(
        label=_("Nombre de la empresa"),
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tech Solutions CA'
        })
    )
    
    rif = forms.CharField(
        label=_("RIF"),
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'J-123456789'
        }),
        help_text=_("Formato: J-XXXXXXXXX")
    )
    
    tipo_empresa = forms.ChoiceField(
        label=_("Tipo de empresa"),
        choices=Empresa.TIPO_EMPRESA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    password1 = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        }),
        help_text=_("Mínimo 8 caracteres")
    )
    
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = _("Mínimo 8 caracteres")
        self.fields['password2'].help_text = None
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nombre_empresa']
        user.tipo_usuario = 'empresa'
        
        if commit:
            user.save()
            # Crear perfil de empresa
            Empresa.objects.create(
                user=user,
                nombre_empresa=self.cleaned_data['nombre_empresa'],
                rif=self.cleaned_data['rif'],
                tipo_empresa=self.cleaned_data['tipo_empresa']
            )
        
        return user


# ========== PROFILE FORMS ==========

class ProfesionalProfileForm(forms.ModelForm):
    """Formulario para editar perfil de profesional"""
    
    # Campos de Usuario
    first_name = forms.CharField(
        label=_("Nombres"),
        max_length=150
    )
    last_name = forms.CharField(
        label=_("Apellidos"),
        max_length=150
    )
    ubicacion = forms.CharField(
        label=_("Ubicación"),
        max_length=200,
        required=False
    )
    
    class Meta:
        model = Profesional
        fields = [
            'titulo_actual',
            'descripcion_personal',
            'sitio_web',
            'linkedin_url',
            'github_url',
            'twitter_url'
        ]
        widgets = {
            'titulo_actual': forms.TextInput(attrs={'class': 'form-input'}),
            'descripcion_personal': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': _('Cuéntanos sobre ti, tus objetivos profesionales...')
            }),
            'sitio_web': forms.URLInput(attrs={'class': 'form-input'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['ubicacion'].initial = user.ubicacion


class EmpresaProfileForm(forms.ModelForm):
    """Formulario para editar perfil de empresa"""
    
    ubicacion = forms.CharField(
        label=_("Ubicación"),
        max_length=200,
        required=False
    )
    
    class Meta:
        model = Empresa
        fields = [
            'descripcion_breve',
            'descripcion_completa',
            'sector',
            'tamano',
            'ano_fundacion',
            'sitio_web',
            'telefono',
            'email_contacto',
            'linkedin_url',
            'facebook_url',
            'instagram_url'
        ]
        widgets = {
            'descripcion_breve': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': _('Descripción corta de tu empresa')
            }),
            'descripcion_completa': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 8,
                'placeholder': _('Descripción detallada de tu empresa, misión, visión...')
            }),
            'sector': forms.TextInput(attrs={'class': 'form-input'}),
            'tamano': forms.Select(attrs={'class': 'form-input'}),
            'ano_fundacion': forms.NumberInput(attrs={'class': 'form-input'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-input'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-input'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-input'}),
        }


class HabilidadForm(forms.ModelForm):
    """Formulario para agregar habilidades"""
    
    class Meta:
        model = Habilidad
        fields = ['nombre', 'nivel']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Python, Django, React...')
            }),
            'nivel': forms.Select(attrs={'class': 'form-input'}),
        }


class EducacionForm(forms.ModelForm):
    """Formulario para agregar educación"""
    
    class Meta:
        model = Educacion
        fields = [
            'institucion',
            'titulo',
            'campo_estudio',
            'fecha_inicio',
            'fecha_fin',
            'en_curso',
            'descripcion'
        ]
        widgets = {
            'institucion': forms.TextInput(attrs={'class': 'form-input'}),
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'campo_estudio': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'en_curso': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class ExperienciaLaboralForm(forms.ModelForm):
    """Formulario para agregar experiencia laboral"""
    
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'empresa',
            'cargo',
            'tipo_empleo',
            'modalidad',
            'fecha_inicio',
            'fecha_fin',
            'trabajo_actual',
            'descripcion'
        ]
        widgets = {
            'empresa': forms.TextInput(attrs={'class': 'form-input'}),
            'cargo': forms.TextInput(attrs={'class': 'form-input'}),
            'tipo_empleo': forms.Select(attrs={'class': 'form-input'}),
            'modalidad': forms.Select(attrs={'class': 'form-input'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'trabajo_actual': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

class HabilidadForm(forms.ModelForm):
    class Meta:
        model = Habilidad
        fields = ['nombre', 'nivel']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Python, Django, React...'),
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'nombre': _('Habilidad'),
            'nivel': _('Nivel de dominio'),
        }

class EducacionForm(forms.ModelForm):
    class Meta:
        model = Educacion
        fields = [
            'institucion',
            'titulo',
            'campo_estudio',
            'fecha_inicio',
            'fecha_fin',
            'en_curso',
            'descripcion',
        ]
        widgets = {
            'institucion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Universidad Central de Venezuela'),
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Ingeniería en Computación'),
            }),
            'campo_estudio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Ciencias de la Computación'),
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'en_curso': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe tu formación académica, logros, proyectos...'),
            }),
        }
        labels = {
            'institucion': _('Institución educativa'),
            'titulo': _('Título obtenido'),
            'campo_estudio': _('Campo de estudio'),
            'fecha_inicio': _('Fecha de inicio'),
            'fecha_fin': _('Fecha de finalización'),
            'en_curso': _('Actualmente estudiando'),
            'descripcion': _('Descripción (opcional)'),
        }

class ExperienciaLaboralForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'empresa',
            'cargo',
            'tipo_empleo',
            'modalidad',
            'fecha_inicio',
            'fecha_fin',
            'trabajo_actual',
            'descripcion',
        ]
        widgets = {
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Tech Solutions CA'),
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Desarrollador Full Stack'),
            }),
            'tipo_empleo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'modalidad': forms.Select(attrs={
                'class': 'form-control',
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: Caracas, Venezuela'),
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'trabajo_actual': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Describe tus responsabilidades, logros y proyectos...'),
            }),
        }
        labels = {
            'empresa': _('Empresa'),
            'cargo': _('Cargo'),
            'tipo_empleo': _('Tipo de empleo'),
            'modalidad': _('Modalidad'),
            'ubicacion': _('Ubicación'),
            'fecha_inicio': _('Fecha de inicio'),
            'fecha_fin': _('Fecha de finalización'),
            'trabajo_actual': _('Trabajo actual'),
            'descripcion': _('Descripción'),
        }