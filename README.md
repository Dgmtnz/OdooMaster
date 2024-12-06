

# OdooMaster

OdooMaster es una aplicación de escritorio desarrollada con PySide6 que simplifica la creación de módulos para Odoo. Esta herramienta permite generar módulos básicos de Odoo con una interfaz gráfica intuitiva, eliminando la necesidad de escribir código repetitivo manualmente.

## Descripción

OdooMaster proporciona una interfaz visual para definir modelos, campos y vistas de Odoo. La aplicación genera automáticamente toda la estructura necesaria del módulo, incluyendo archivos Python, vistas XML y configuraciones de seguridad. Además, crea un script bash para facilitar la instalación en sistemas Linux.

### Características principales:
- Interfaz gráfica intuitiva para la definición de módulos
- Creación de múltiples modelos por módulo
- Soporte para diversos tipos de campos (Char, Integer, Float, Boolean, etc.)
- Generación automática de vistas (form, tree)
- Creación de menús y submenús
- Generación de permisos básicos
- Script bash para instalación rápida

## Capturas de pantalla

![image](https://github.com/user-attachments/assets/4658b56f-e71b-4b50-a915-6e4f489ed1cd)


## Requisitos

- Python 3.8 o superior
- PySide6
- Sistema operativo compatible (Windows, Linux, macOS)
- Odoo 17.0 (para la instalación de los módulos generados)

## Instalación

1. Clona este repositorio:

```bash
git clone https://github.com/dgmtnz/OdooMaster.git
```

2. Instala las dependencias:

```bash
pip install PySide6
```

3. Ejecuta la aplicación:

```bash
python main_window.py
```

## Uso

1. Inicia OdooMaster
2. Define la información básica del módulo (nombre, versión, categoría)
3. Añade los modelos necesarios usando el botón "Add Model"
4. Para cada modelo:
   - Define el nombre técnico del modelo
   - Añade los campos necesarios
   - Configura las propiedades de cada campo
5. Haz clic en "Generate Module" para crear el módulo
6. Elige la ubicación donde guardar el módulo generado

### Instalación del módulo generado

OdooMaster genera dos elementos:
1. La carpeta del módulo con toda la estructura necesaria
2. Un script bash (`create_[nombre_modulo]_module.sh`) para instalar el módulo en sistemas Linux

Para instalar usando el script:

```bash
sudo chmod +x create_[nombre_modulo]module.sh
sudo ./create_[nombre_modulo]module.sh
```


## Licencia

Este proyecto está bajo la licencia GPL (Licencia Pública General de GNU). Puedes copiar, modificar y distribuir el código, siempre que mantengas la misma licencia y hagas público cualquier cambio realizado.

## Soporte

Si encuentras algún problema o tienes sugerencias para OdooMaster, no dudes en abrir un issue en este repositorio. Tu feedback es importante para mejorar esta herramienta.

## Créditos

- Desarrollado por Diego Martínez Fernández (@Dgmtnz)
- Construido con PySide6 y Python
- Diseñado para Odoo 17.0

¡Gracias por usar OdooMaster! Espero que esta herramienta te ayude a agilizar el desarrollo de módulos para Odoo.

