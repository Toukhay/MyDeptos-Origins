# MyDeptosFinal

**MyDeptosFinal** es un proyecto *WEB-APP* que trata de una página de departamentos desarrollado utilizando HTML, CSS, JavaScript, y Flask como backend, con MySQL como base de datos. El proposito surgio en el intentar siendo un estudiante junto con mi compañera poder lograr resolver la famosa pregunta cuando estas en una ciudad siendo trabajador, estudiante, ¿Donde puedo encontrar un departamento disponible cerca de la zona? 

## Tecnologías Utilizadas

- **HTML**: Para la estructura de las páginas web.
- **CSS**: Para el estilo y diseño de la interfaz de usuario.
- **JavaScript**: Para la interactividad en el lado del cliente.
- **Flask**: Framework de Python para el backend.
- **MySQL**: Base de datos relacional para almacenar la información de los departamentos.
- **XAMPP**: Herramienta utilizada para crear un servidor local que facilita la ejecución de MySQL y PHP.


### Pasos para ejecutar el proyecto

1. **Clona el repositorio** en tu máquina local:

    ```bash
    git clone https://github.com/Toukhay/MyDeptosFinal.git
    ```

2. **Configura la base de datos**:
   - Asegúrate de que XAMPP esté ejecutándose y MySQL esté activo.
   - Accede a phpMyAdmin (usualmente en `http://localhost/phpmyadmin`) y crea una base de datos para el proyecto.
   - Configura la conexión a la base de datos en el proyecto (probablemente en un archivo de configuración de Flask).
   - Si tienes un archivo SQL de ejemplo, impórtalo en la base de datos.

3. **Instala las dependencias de Python**:
   - Navega a la carpeta del proyecto:

     ```bash
     cd MyDeptosFinal
     ```

   - Crea un entorno virtual (opcional, pero recomendado):

     ```bash
     python -m venv venv
     ```

   - Activa el entorno virtual:
     - En Windows:

       ```bash
       venv\Scripts\activate
       ```

   - Instala las dependencias necesarias:

     ```bash
     pip install -r requirements.txt
     ```

4. **Ejecuta el servidor Flask**:

    ```bash
    python app.py
    ```

    Esto iniciará el servidor Flask, y podrás acceder al proyecto en tu navegador en:

    ```
    http://localhost:5000
    ```

## Contribuciones

Si deseas contribuir al proyecto, por favor sigue estos pasos:

1. Haz un fork de este repositorio.
2. Crea una nueva rama para tus cambios.
3. Realiza tus cambios y haz un commit con una descripción clara.
4. Envía un pull request.

## Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).
