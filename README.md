# 🏢 MyDeptos - Sistema de Gestión Inmobiliaria

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**MyDeptos** es una plataforma profesional para la gestión de inmuebles en Misiones, Argentina. Este proyecto representa la transición de una arquitectura monolítica local a una infraestructura cloud escalable y containerizada.

🔗 **[Explorar Proyecto en Vivo](https://mydeptos-origins-production.up.railway.app/)**

---

## 🚀 Desafíos Técnicos Superados (Fase de Deploy)
Como **Analista Programador**, el despliegue de este proyecto implicó resolver retos de ingeniería real:
* **Orquestación con Docker:** Creación de imágenes optimizadas (`python:3.11-slim`) para reducir el footprint en producción.
* **Infraestructura como Código (IaC):** Configuración de despliegue automatizado mediante `railway.json` para garantizar la paridad entre entornos de desarrollo y producción.
* **Networking Dinámico:** Implementación de un shell wrapper para la inyección de variables de entorno de puerto (`$PORT`) en el servidor **Gunicorn**, permitiendo el bindeo dinámico requerido por los orquestadores modernos.
* **Persistencia de Datos:** Migración exitosa de un esquema de desarrollo en MySQL a una base de datos **PostgreSQL** productiva utilizando **Flask-Migrate (Alembic)**.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Implementación |
|------|-----------|----------------|
| **Backend** | Python 3.11 | Flask con Blueprints (Arquitectura Modular) |
| **Server** | Gunicorn | Manejo de peticiones concurrentes en producción |
| **Database** | PostgreSQL 16 | SQLAlchemy ORM + Migraciones controladas |
| **Seguridad** | Bcrypt & CSRF | Hashing de passwords y protección de formularios |
| **Maps** | Leaflet.js | Geolocalización de unidades en tiempo real |
| **Infraestructura**| Docker | Containerización completa del stack |

---

## 📐 Arquitectura de la Solución

El proyecto utiliza una estructura de **Application Factory**, lo que permite una fácil expansión de módulos (Auth, Admin, Deptos) sin acoplamiento de código.

---

## ⚙️ Instalación y Replicabilidad

### Entorno de Desarrollo (Docker Compose)
```bash
git clone [https://github.com/Toukhay/MyDeptos-Origins.git](https://github.com/Toukhay/MyDeptos-Origins.git)
cd MyDeptos-Origins
docker compose up --build

El proyecto cuenta con una suite de 11 tests automatizados cubriendo flujos críticos de autenticación y navegación.

python -m pytest tests/ -v

