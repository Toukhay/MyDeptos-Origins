# MyDeptos

Plataforma web para publicar y encontrar departamentos en alquiler o venta. Desarrollada con Flask y MySQL, orientada a estudiantes y trabajadores que buscan alojamiento.

## Stack tecnológico

- **Backend**: Python 3 + Flask
- **Base de datos**: MySQL (XAMPP en desarrollo local)
- **Frontend**: HTML, CSS, JavaScript
- **Autenticación**: Flask-Login + bcrypt
- **Formularios**: WTForms con validación backend
- **Seguridad**: CSRF protection, variables de entorno, hash de contraseñas

## Funcionalidades

- Registro, login y recuperación de contraseña por email
- Publicación, edición y eliminación de departamentos con fotos
- Búsqueda avanzada con filtros (precio, ambientes, localidad, distancia geográfica)
- Sistema de favoritos y reseñas
- Notificaciones internas
- Panel de administración
- Paginación en listados

## Arquitectura

El proyecto está organizado en módulos usando Flask Blueprints:
```
MyDeptos-Origins/
├── app.py                  # Entry point, factory function
├── config.py               # Configuración centralizada
├── extensions.py           # Extensiones Flask (MySQL, Login, CSRF)
├── forms.py                # Formularios WTForms
├── utils.py                # Funciones helper (email, etc.)
├── routes/
│   ├── auth.py             # Login, registro, recuperación de contraseña
│   ├── main.py             # Home, búsqueda, listings
│   ├── deptos.py           # Publicaciones y reseñas
│   ├── user.py             # Panel de usuario, favoritos, notificaciones
│   └── admin.py            # Panel de administración
├── templates/              # HTML con Jinja2
├── static/                 # CSS, JS, imágenes
├── database.sql            # Schema de base de datos
└── requirements.txt        # Dependencias Python
```

## Instalación local

**1. Clonar el repositorio**
```bash
git clone https://github.com/Toukhay/MyDeptos-Origins.git
cd MyDeptos-Origins
```

**2. Instalar dependencias**
```bash
python -m pip install -r requirements.txt
```

**3. Configurar variables de entorno**

Crear un archivo `.env` en la raíz del proyecto:
```
SECRET_KEY=una_clave_secreta_larga
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=bdmydeptos
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
```

**4. Crear la base de datos**

Con XAMPP corriendo, importar `database.sql` desde phpMyAdmin (`http://localhost/phpmyadmin`).

**5. Ejecutar**
```bash
python app.py
```

Accedé en [http://localhost:5000](http://localhost:5000)

## Changelog

### Fase 1 — Refactor de estructura (2026-03)
- Separación de `app.py` (~1800 líneas) en módulos usando Flask Blueprints
- Configuración centralizada en `config.py` con validación de variables críticas
- Extensiones Flask desacopladas en `extensions.py`
- Formularios centralizados en `forms.py`
- Funciones helper en `utils.py` — eliminadas credenciales hardcodeadas
- Reemplazados todos los `print()` de debug por `app.logger`
- Agregado `database.sql` con schema completo y datos iniciales
- Limpieza de `requirements.txt` — eliminadas dependencias sin uso

## Seguridad

Consultar [SECURITY.md](SECURITY.md) para detalles sobre prácticas y reporte de vulnerabilidades.

## Licencia

MIT License.