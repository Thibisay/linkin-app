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