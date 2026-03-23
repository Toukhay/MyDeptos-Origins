# MyDeptos

Plataforma web para publicar y encontrar departamentos en alquiler o venta en Misiones, Argentina.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Tests](https://img.shields.io/badge/Tests-11%20passing-brightgreen)

## Demo

🔗 **[Ver proyecto en vivo](TU_URL_AQUI)** ← se completa en el Paso de deploy

## Funcionalidades

- Registro, login y recuperación de contraseña por email
- Publicación de departamentos con fotos, precio, ubicación y filtros
- Búsqueda avanzada con filtros por tipo, precio, ambientes, localidad y distancia geográfica (Haversine)
- Sistema de favoritos y reseñas con notificaciones internas
- Panel de administración completo
- Paginación en todos los listados

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + Flask 3.1 |
| ORM | SQLAlchemy + Alembic |
| Base de datos | PostgreSQL 16 |
| Autenticación | Flask-Login + bcrypt |
| Formularios | WTForms con validación backend |
| Seguridad | CSRF protection, variables de entorno |
| Contenedores | Docker + Docker Compose |
| Tests | pytest + pytest-flask (11 tests) |

## Arquitectura
```
MyDeptos/
├── app.py                  # Entry point, application factory
├── config.py               # Configuración centralizada
├── extensions.py           # Extensiones Flask
├── forms.py                # Formularios WTForms
├── models.py               # Modelos SQLAlchemy
├── utils.py                # Funciones helper
├── routes/
│   ├── auth.py             # Login, registro, recuperación de contraseña
│   ├── main.py             # Home, búsqueda, listings
│   ├── deptos.py           # Publicaciones y reseñas
│   ├── user.py             # Panel de usuario, favoritos, notificaciones
│   └── admin.py            # Panel de administración
├── tests/
│   ├── conftest.py         # Configuración de tests
│   └── test_auth.py        # Tests de autenticación y rutas
├── templates/              # HTML con Jinja2
├── static/                 # CSS, JS, imágenes
├── migrations/             # Migraciones Alembic
├── Dockerfile
├── docker-compose.yml
└── database.sql            # Schema inicial
```

## Instalación local con Docker

**Requisitos**: Docker y Docker Compose instalados.
```bash
git clone https://github.com/Toukhay/MyDeptos-Origins.git
cd MyDeptos-Origins
docker compose up --build
```

Accedé en [http://localhost:5000](http://localhost:5000)

## Instalación local sin Docker

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

Crear `.env` en la raíz:
```
SECRET_KEY=una_clave_secreta_larga
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/mydeptos
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
```

**4. Crear la base de datos**
```bash
flask db upgrade
```

**5. Ejecutar**
```bash
python app.py
```

## Tests
```bash
python -m pytest tests/ -v
```
```
tests/test_auth.py::test_home_page_loads PASSED
tests/test_auth.py::test_login_page_loads PASSED
tests/test_auth.py::test_register_page_loads PASSED
tests/test_auth.py::test_login_with_wrong_credentials PASSED
tests/test_auth.py::test_register_new_user PASSED
tests/test_auth.py::test_register_duplicate_username PASSED
tests/test_auth.py::test_user_panel_requires_login PASSED
tests/test_auth.py::test_admin_panel_requires_login PASSED
tests/test_auth.py::test_favorites_requires_login PASSED
tests/test_auth.py::test_authenticated_user_can_access_panel PASSED
tests/test_auth.py::test_listings_page_loads PASSED
```

## Changelog

### Fase 5 — Deploy (2026-03)
- README profesional con badges y documentación completa
- Deploy en Railway con PostgreSQL

### Fase 4 — Tests (2026-03)
- 11 tests con pytest y pytest-flask
- Tests de autenticación, rutas protegidas y registro

### Fase 3 — Docker (2026-03)
- Dockerfile y docker-compose.yml
- Entorno reproducible con un solo comando

### Fase 2 — SQLAlchemy + PostgreSQL (2026-03)
- Migración de MySQL a PostgreSQL
- ORM con SQLAlchemy y migraciones con Alembic

### Fase 1 — Refactor (2026-03)
- Separación de app.py en Flask Blueprints
- Configuración centralizada y limpieza general

## Licencia

MIT License.
```

Guardá con `Ctrl + S`.

---

### Paso 3 — Deploy en Railway

Railway es la plataforma más simple para deployar Flask + PostgreSQL gratis.

**1.** Entrá a `https://railway.app` y hacé click en **Login with GitHub**.

**2.** Una vez dentro, click en **New Project** → **Deploy from GitHub repo**.

**3.** Seleccioná `MyDeptos-Origins`.

**4.** Railway va a detectar el `Dockerfile` automáticamente. Antes de deployar, necesitás agregar las variables de entorno. Click en el servicio → **Variables** → agregá:
```
SECRET_KEY=mydeptos_production_secret_key_2026
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=noconfigurado
```

**5.** Para la base de datos, click en **New** → **Database** → **PostgreSQL**. Railway crea la base de datos y automáticamente agrega `DATABASE_URL` como variable de entorno.

**6.** Una vez deployado, necesitás correr las migraciones. Click en el servicio web → **Deploy** → **Run command**:
```
flask db upgrade