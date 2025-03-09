# Explicación de Archivos en MyDeptosFlask

Este documento proporciona una visión general de la estructura y el propósito de cada archivo en la carpeta `MyDeptosFlask`. Puedes personalizar y expandir esta explicación según tus necesidades.

## Archivos Principales

### `app.py`

Este es el archivo principal de la aplicación Flask. Define las rutas y la lógica de negocio para la aplicación. Algunas de las rutas importantes incluyen:

- `/publish_depto`: Maneja la publicación de departamentos, incluyendo la subida de múltiples fotos.
- `/listings`: Muestra una lista de departamentos publicados con un carrusel de imágenes.
- `/viewProperty`: Muestra los detalles de una propiedad específica.

### `forms.py`

Este archivo define los formularios utilizados en la aplicación utilizando Flask-WTF. Incluye el formulario `PublishDeptoForm` que maneja la validación y la subida de múltiples fotos para la publicación de departamentos.

## Plantillas HTML

### `templates/about.html`

Esta plantilla muestra información sobre la aplicación o la empresa. Puede incluir detalles sobre la misión, visión y equipo.

### `templates/base.html`

Esta es la plantilla base que otras plantillas extienden. Incluye elementos comunes como el encabezado, pie de página y enlaces a archivos CSS y JavaScript.

### `templates/dashboard.html`

Esta plantilla muestra el dashboard principal de la aplicación, donde los usuarios pueden navegar a diferentes secciones como su perfil, favoritos, lista de departamentos y publicar un nuevo departamento.

### `templates/edit_profile.html`

Esta plantilla contiene el formulario para que los usuarios editen su perfil. Incluye campos para actualizar la información personal y la contraseña.

### `templates/forgotpassword.html`

Esta plantilla contiene el formulario para que los usuarios soliciten un restablecimiento de contraseña. Incluye un campo para ingresar el correo electrónico.

### `templates/generate_password.html`

Esta plantilla permite a los usuarios generar una contraseña segura. Puede incluir un botón para generar una nueva contraseña y mostrarla en pantalla.

### `templates/home.html`

Esta es la página de inicio de la aplicación. Puede incluir una introducción a la aplicación y enlaces a las principales funcionalidades.

### `templates/listings.html`

Esta plantilla muestra la lista de departamentos publicados. Cada departamento se muestra con un carrusel de imágenes y detalles como el título, descripción, tipo de publicación, precio, ambientes, dormitorios, baños, superficie, dirección y fecha de publicación. Incluye estilos CSS para mejorar la apariencia de la lista y un script para manejar el carrusel de imágenes.

### `templates/publish_depto.html`

Esta plantilla contiene el formulario HTML para la publicación de departamentos. Incluye campos para el título, descripción, tipo de publicación, precio, moneda, ambientes, dormitorios, baños, superficie, dirección, localidad y fotos del departamento. También incluye estilos CSS para mejorar la apariencia del formulario y un script para ocultar los mensajes flash después de 5 segundos.

### `templates/register.html`

Esta plantilla contiene el formulario de registro para nuevos usuarios. Incluye campos para el nombre, correo electrónico y contraseña.

### `templates/resetpassword.html`

Esta plantilla contiene el formulario para que los usuarios restablezcan su contraseña. Incluye campos para ingresar la nueva contraseña y confirmarla.

### `templates/search_results.html`

Esta plantilla muestra los resultados de búsqueda de departamentos. Incluye una lista de departamentos que coinciden con los criterios de búsqueda ingresados por el usuario.

### `templates/user_panel.html`

Esta plantilla muestra el panel de usuario, donde los usuarios pueden ver y editar su perfil, así como ver sus departamentos publicados.

### `templates/viewproperty.html`

Esta plantilla muestra los detalles de una propiedad específica. Incluye información como la dirección, precio, descripción, número de habitaciones, baños y área.

## Archivos Estáticos

### `static/image/`

Esta carpeta contiene las imágenes subidas por los usuarios para los departamentos. Asegúrate de que esta carpeta exista y tenga los permisos adecuados para guardar las fotos.

## Archivo de Configuración

### `.env`

Este archivo contiene las variables de entorno necesarias para configurar la aplicación Flask. Incluye configuraciones como el nombre de la aplicación, el entorno de desarrollo, la clave secreta y las credenciales de la base de datos MySQL.

## Archivo de Requisitos

### `requirements.txt`

Este archivo lista todas las dependencias necesarias para ejecutar la aplicación. Incluye paquetes como Flask, Flask-WTF y Flask-MySQLdb. Puedes instalar todas las dependencias ejecutando `pip install -r requirements.txt`.

## Estructura del Proyecto
