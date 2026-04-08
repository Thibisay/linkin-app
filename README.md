### [ATI-EC Linking X](https://drive.google.com/file/d/1cE1w9WHLHbG8QmHsql6GokdtjXBL_FqM/view?usp=drive_link)
<img width="360" height="140" alt="banner_logo" src="https://github.com/user-attachments/assets/b0607340-8004-48b4-abcf-7a9d3c758324" />

![Django](https://img.shields.io/badge/Django-6.0.1-green?style=flat&logo=django)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=flat&logo=docker)
![Status](https://img.shields.io/badge/Status-Design-orange)

ATI-EC Linking X es una red social desarrollada en Django/SQLite para conectar profesionales de ATI-UCV con empresas.  
Incluye perfiles personalizados, muro de publicaciones multimedia, chat en tiempo real, sistema de notificaciones y módulo de administración de contenidos.  
Utiliza metodologías ágiles (Scrum) y casos de uso para gestionar perfiles profesionales y ofertas de empleo, optimizando la inserción laboral.

---

## Tecnologías (Requisitos No funcionales)
- Backend: Python 3.12 + Django 6.0.1  
- Base de Datos: SQLite (Entorno de Desarrollo)  
- Infraestructura: Docker & Docker Compose  
- Control de Versiones: Git & GitHub  

---

## Configuración del Entorno (Instalación)

1. Prerrequisitos

- Tener instalado [Docker](https://www.docker.com/) y Docker Compose.  
- Tener instalado [Git](https://git-scm.com/).  

2. Clonar el Repositorio
```bash
git clone https://github.com/Mattw-Xproject/ATI-Proy-EC-Linkin.git
```
3. Levantar con Docker (La forma fácil)

No necesitas instalar Python ni crear entornos virtuales manualmente. Docker se encarga de todo.

- Para iniciar el servidor: ```bash sudo docker compose up ```
- El sistema estará disponible en: http://localhost
- Si no levanta o agregaste nuevas librerías: Si la imagen no carga o modificaste el requirements.txt, fuerza la reconstrucción: 
```bash
sudo docker compose up -d --build
```
4. Ejecutar Tests

- Para correr las pruebas unitarias dentro del contenedor (en otra terminal, mientras el servidor está corriendo):
```bash
sudo docker compose exec web python manage.py test
```
## Diagrama de Clases de Linking X
<img width="1503" height="1322" alt="diagrama-de-clases drawio-3" src="https://github.com/user-attachments/assets/12c83684-c737-4721-9d0b-ae8369ca9c7b" />

## Mapa de navegación Linking X

<img width="2466" height="576" alt="Mapa de navegación Linking X drawio" src="https://github.com/user-attachments/assets/e5d3bae0-a2ce-414f-bb17-332b1c9a2de5" />

## Diagrama de paquetes(o de componentes de un proyecto Django + MVT)
<img width="2809" height="1048" alt="Diagrama de Arquitectura (de paquetes y componentes)" src="https://github.com/user-attachments/assets/1480adc2-33f7-453d-a222-cd90e39f34f0" />

## Fragmentos de Casos de Uso mas importantes
<img width="1460" height="505" alt="Fragmento 01 1_UC1" src="https://github.com/user-attachments/assets/94768859-019a-4808-8cbf-84d4aba88f9c" />
<img width="1472" height="536" alt="Fragmento 05 1_UC5" src="https://github.com/user-attachments/assets/c6001707-be3d-46d5-b8be-56287c790c33" />

### Para un perfil empresa/profesional ya registrado

<img width="349" height="113" alt="Fragmento CU07" src="https://github.com/user-attachments/assets/90dffc42-8bec-479a-bfdd-b6f1e1f1b29b" />
<img width="295" height="102" alt="Fragmento CU08" src="https://github.com/user-attachments/assets/32c16b22-ebaa-42cc-856c-8063e21e1cd4" />
<img width="262" height="147" alt="Fragmento CU10 2" src="https://github.com/user-attachments/assets/3987b380-31d5-47a8-8238-206c55baed3c" />

### Para moderacion de contenido de las publicaciones/comentarios para el administrador

<img width="439" height="106" alt="Fragmento CU11-12(Admin sobre Publicaciones)" src="https://github.com/user-attachments/assets/62d2525a-6f5d-48cf-9151-b322cc6c3e1d" />
<img width="355" height="84" alt="Fragmento CU13-14 (Admin sobre Comentarios)" src="https://github.com/user-attachments/assets/5d91ebda-34d3-4afd-91df-fade65e2b7ee" />
