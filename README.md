# MyDeptosFinal

**MyDeptosFinal** es una *WEB-APP* para encontrar y publicar departamentos, pensada para estudiantes y trabajadores que buscan alojamiento en una ciudad.

## Tecnologías Utilizadas

- **HTML, CSS, JavaScript**: Frontend.
- **Flask**: Backend en Python.
- **MySQL**: Base de datos.
- **XAMPP**: Servidor local para MySQL.

## Estructura del Proyecto

- `/static/css/`: Hojas de estilo.
- `/templates/`: Archivos HTML de las vistas.
- `app.py`: Lógica principal de la aplicación.
- `requirements.txt`: Dependencias de Python.
- `SECURITY.md`: Política de seguridad.
- `README.md`: Documentación principal.

## Funcionalidades Principales

- Registro y login de usuarios.
- Recuperación y cambio de contraseña.
- Publicación, edición y eliminación de departamentos.
- Favoritos y notificaciones.
- Panel de administración para gestión de usuarios y departamentos.
- Paginación y búsqueda avanzada.
- Seguridad: hash de contraseñas, protección CSRF, validación de datos.

## Instalación y Ejecución

1. **Clona el repositorio**:

    ```bash
    git clone https://github.com/Toukhay/MyDeptosFinal.git
    ```

2. **Configura la base de datos**:
   - Usa XAMPP y phpMyAdmin para crear la base de datos.
   - Importa el archivo SQL si está disponible.

3. **Instala dependencias**:

    ```bash
    cd MyDeptosFinal
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

4. **Ejecuta el servidor Flask**:

    ```bash
    python app.py
    ```

    Accede en [http://localhost:5000](http://localhost:5000)

## Pruebas

Actualmente las pruebas son manuales. Para contribuir con tests automáticos, crea archivos en `/tests/` y usa `pytest`.

## Seguridad

Consulta [SECURITY.md](SECURITY.md) para detalles sobre prácticas y reporte de vulnerabilidades.

## Contribuciones

1. Haz un fork.
2. Crea una rama.
3. Haz tus cambios y crea un pull request.

## Licencia

MIT License.

## Preguntas Frecuentes (FAQ)

**¿Qué hago si la aplicación no inicia?**  
- Verifica que tengas Python 3 instalado y que hayas activado el entorno virtual.
- Revisa que la base de datos esté creada y configurada correctamente en XAMPP.

**¿Cómo recupero mi contraseña?**  
- Haz clic en "¿Olvidaste tu contraseña?" en la página de login y sigue los pasos.

**¿Puedo publicar más de un departamento?**  
- Sí, cada usuario puede publicar varios departamentos desde su panel.

**¿Cómo elimino mi cuenta?**  
- Solicita la eliminación desde el panel de usuario o contacta al administrador.

**¿Dónde reporto errores o sugerencias?**  
- Crea un "Issue" en GitHub o envía un correo a facu-202020@hotmail.com.

---

## Ejemplos de Uso

**Registro de usuario:**
1. Accede a la página principal.
2. Haz clic en "Registrarse".
3. Completa el formulario y confirma tu correo.

**Publicar un departamento:**
1. Inicia sesión.
2. Ve al panel de usuario y selecciona "Publicar departamento".
3. Completa los datos y sube imágenes.

**Agregar a favoritos:**
1. Busca departamentos en la página principal.
2. Haz clic en el ícono de "favorito" para guardar el departamento en tu lista.

**Recuperar contraseña:**
1. Haz clic en "¿Olvidaste tu contraseña?".
2. Ingresa tu correo y sigue las instrucciones enviadas.

**Acceso como administrador:**
1. Inicia sesión con una cuenta de administrador.
2. Accede al panel de administración para gestionar usuarios y departamentos.