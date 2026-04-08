# Guía de Contribución - ATI-EC Linking

## 1. Política de Ramas (Branching Model)

Para que el CI/CD (GitHub Actions) verifique el código, las ramas DEBEN seguir este formato:

- Features: "feature/nombre-funcionalidad" 
  Ejemplo: "feature/login-usuario"
- Desarrollo: "dev/nombre-dev/descripcion"  
  Ejemplo: "dev/ati/form-perfil"
- Hotfix: "fix/descripcion-error"  
  Ejemplo: "fix/corregir-bug-login"

> [!IMPORTANT]
> Nunca hagas push directo a "main" o "develop". Usa Pull Requests.

---

## 2. Estándar de Commits

Usamos Conventional Commits + referencia a Reto/Caso de Uso.

- Formato:
[Reto ##] UC-XX tipo_alcance Verbo infinitivo + Descripción

- Tipos permitidos (en inglés):
- "feat": nueva funcionalidad.
- "fix": corrección de error.
- "docs": cambios en documentación.
- "style": cambios de formato (PEP8, indentación).
- "refactor": mejoras internas sin cambiar lógica.
- "chore": tareas de configuración (Docker, dependencias).
- "create": crear archivos base.
- "add": agregar implementación a algo existente.
- "change": mejoras en estilos o código.

- Ámbitos (ejemplos):
- "DOCKER", "MODELS", "VIEWS", "AUTH", etc.

> [!TIP]
> - [Reto 13] UC-01 feat_auth Agregado login con django_auth
> - [Reto 12] UC-04 fix_model Corregir relación en tabla Users
> - [Reto 10] chore_docker Configuración inicial de Dockerfile

---

## 3. Estilo de Código (PEP8)

Todo el equipo debe seguir el estándar PEP8 para Python:

- Indentación: 4 espacios por nivel (no usar tabuladores).

- Longitud máxima de línea: 79 caracteres (Django permite hasta 119, pero intentemos mantenerlo corto).

- Imports al inicio del archivo, ordenados: 

1. Librerías estándar (os, sys).
2. Librerías de terceros (django, rest_framework).
3. Importaciones locales (from .models import Usuario).

- Variables y funciones en snake_case (ej: calcular_promedio).

- Clases en CamelCase (ej: PerfilUsuario).

- Espacios: dejar una línea en blanco entre funciones y clases, y alrededor de imports.

- Comentarios: claros y en español, usando # al inicio.

- Formateo automático: usar Black para dar formato al guardar.

- Linting: usar Flake8 para detectar errores antes de hacer push.

> [!NOTE]
> Configura tu editor (VSCode recomendado) con Black Formatter y activa “Format on Save” para no perder tiempo corrigiendo manualmente.

---

## 4. Checklist antes de hacer commit
> [!WARNING]
> - Correr los tests (pytest o manage.py test).
> - Formatear el código con black ..
> - Validar con flake8 ..
- Escribir el commit siguiendo la convención.

---

## 5. Documentación y Estilos

- Estilo de código: seguimos PEP8 estrictamente [La Guía de Estilos en Python.](https://elpythonista.com/pep-8)

- Consulta la [Wiki del Proyecto](https://github.com/Mattw-Xproject/ATI-Proy-EC-Linkin/wiki/Gu%C3%ADa-de-Estilo-Python-(PEP8)) para ver configuración de linters en VSCode.

- Usa la extensión Black Formatter en tu editor para formateo automático.

