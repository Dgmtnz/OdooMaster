# Importamos los widgets necesarios de PySide6
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLineEdit, QLabel, QComboBox, 
                              QTableWidget, QTableWidgetItem, QSpinBox,
                              QCheckBox, QMessageBox, QFileDialog, QApplication)
from PySide6.QtCore import Qt
import os
import sys

class ModelFieldWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)  # Changed to VBoxLayout for better organization
        
        # Main field properties layout
        main_layout = QHBoxLayout()
        
        # Campo para el nombre
        self.name = QLineEdit()
        self.name.setPlaceholderText("Field Name")
        
        # Tipo de campo
        self.field_type = QComboBox()
        self.field_type.addItems([
            'Char', 'Text', 'Integer', 'Float', 'Boolean', 
            'Date', 'Datetime', 'Selection', 'Many2one'
        ])
        
        # Required checkbox
        self.required = QCheckBox("Required")
        
        # String (label)
        self.string = QLineEdit()
        self.string.setPlaceholderText("Field Label")
        
        # Añadir widgets al layout principal
        main_layout.addWidget(self.name)
        main_layout.addWidget(self.field_type)
        main_layout.addWidget(self.string)
        main_layout.addWidget(self.required)
        layout.addLayout(main_layout)
        
        # Selection options widget (initialize before connecting signal)
        self.selection_layout = QVBoxLayout()
        self.selection_options = []
        self.add_selection_btn = QPushButton("Add Selection Option")
        self.add_selection_btn.clicked.connect(self.add_selection_option)
        self.add_selection_btn.hide()
        layout.addLayout(self.selection_layout)
        layout.addWidget(self.add_selection_btn)
        
        # Validation layout
        self.validation_layout = QHBoxLayout()
        layout.addLayout(self.validation_layout)
        
        # Initialize validation widgets
        self.init_validation_widgets()
        
        # Connect signal after all widgets are initialized
        self.field_type.currentTextChanged.connect(self.on_field_type_changed)
        self.on_field_type_changed(self.field_type.currentText())

    def init_validation_widgets(self):
        # Numeric validation
        self.min_value = QSpinBox()
        self.min_value.setMinimum(-999999)
        self.min_value.setMaximum(999999)
        self.min_value.setValue(0)
        self.min_value.setPrefix("Min: ")
        
        self.max_value = QSpinBox()
        self.max_value.setMinimum(-999999)
        self.max_value.setMaximum(999999)
        self.max_value.setValue(100)
        self.max_value.setPrefix("Max: ")
        
        # String validation
        self.min_length = QSpinBox()
        self.min_length.setMinimum(0)
        self.min_length.setMaximum(1000)
        self.min_length.setPrefix("Min Length: ")
        
        self.max_length = QSpinBox()
        self.max_length.setMinimum(0)
        self.max_length.setMaximum(1000)
        self.max_length.setValue(100)
        self.max_length.setPrefix("Max Length: ")

    def on_field_type_changed(self, field_type):
        # Clear current validation widgets
        while self.validation_layout.count():
            item = self.validation_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
        
        # Add appropriate validation widgets based on field type
        if field_type in ['Integer', 'Float']:
            self.validation_layout.addWidget(self.min_value)
            self.validation_layout.addWidget(self.max_value)
            self.min_value.show()
            self.max_value.show()
        elif field_type in ['Char', 'Text']:
            self.validation_layout.addWidget(self.min_length)
            self.validation_layout.addWidget(self.max_length)
            self.min_length.show()
            self.max_length.show()
        
        # Show/hide selection options based on field type
        self.add_selection_btn.setVisible(field_type == 'Selection')
        
        # Hide all selection options if not Selection type
        for i in range(self.selection_layout.count()):
            layout = self.selection_layout.itemAt(i)
            if layout:
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if widget:
                        widget.setVisible(field_type == 'Selection')

    def get_validation_code(self):
        field_type = self.field_type.currentText()
        validation_code = []
        
        if field_type in ['Integer', 'Float']:
            min_val = self.min_value.value()
            max_val = self.max_value.value()
            if min_val != 0 or max_val != 100:
                validation_code.append(f"""
    @api.constrains('{self.name.text()}')
    def _check_{self.name.text()}_value(self):
        for record in self:
            if record.{self.name.text()}:
                if record.{self.name.text()} < {min_val} or record.{self.name.text()} > {max_val}:
                    raise ValidationError(f'El valor de {self.string.text()} debe estar entre {min_val} y {max_val}')
""")
        
        elif field_type in ['Char', 'Text']:
            min_len = self.min_length.value()
            max_len = self.max_length.value()
            if min_len != 0 or max_len != 100:
                validation_code.append(f"""
    @api.constrains('{self.name.text()}')
    def _check_{self.name.text()}_length(self):
        for record in self:
            if record.{self.name.text()}:
                if len(record.{self.name.text()}) < {min_len} or len(record.{self.name.text()}) > {max_len}:
                    raise ValidationError(f'La longitud de {self.string.text()} debe estar entre {min_len} y {max_len} caracteres')
""")
        
        return validation_code

    def add_selection_option(self):
        option_layout = QHBoxLayout()
        
        # Key input
        key = QLineEdit()
        key.setPlaceholderText("Option Key (e.g., 'draft')")
        
        # Value input
        value = QLineEdit()
        value.setPlaceholderText("Option Label (e.g., 'Draft')")
        
        # Remove button
        remove_btn = QPushButton("X")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_selection_option(option_layout))
        
        option_layout.addWidget(key)
        option_layout.addWidget(value)
        option_layout.addWidget(remove_btn)
        
        self.selection_layout.addLayout(option_layout)
        self.selection_options.append((key, value))

    def remove_selection_option(self, layout):
        # Remove the option from the list and UI
        for i in range(self.selection_layout.count()):
            if self.selection_layout.itemAt(i) == layout:
                self.selection_options.pop(i)
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                break
        

class ModelWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Nombre del modelo
        model_layout = QHBoxLayout()
        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText("Model Name (e.g., res.partner)")
        model_layout.addWidget(QLabel("Model:"))
        model_layout.addWidget(self.model_name)
        layout.addLayout(model_layout)
        
        # Lista de campos
        self.fields = []
        self.fields_layout = QVBoxLayout()
        layout.addLayout(self.fields_layout)
        
        # Botón para añadir campo
        add_field_btn = QPushButton("Add Field")
        add_field_btn.clicked.connect(self.add_field)
        layout.addWidget(add_field_btn)
        
        self.add_field()  # Añadir un campo inicial

    def add_field(self):
        field = ModelFieldWidget()
        self.fields.append(field)
        self.fields_layout.addWidget(field)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OdooMaster - Module Generator")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Información básica del módulo
        module_info = QWidget()
        module_layout = QVBoxLayout(module_info)
        
        # Nombre del módulo
        name_layout = QHBoxLayout()
        self.module_name = QLineEdit()
        self.module_name.setPlaceholderText("Module Name")
        name_layout.addWidget(QLabel("Module Name:"))
        name_layout.addWidget(self.module_name)
        module_layout.addLayout(name_layout)
        
        # Versión
        version_layout = QHBoxLayout()
        self.version = QLineEdit("1.0")
        version_layout.addWidget(QLabel("Version:"))
        version_layout.addWidget(self.version)
        module_layout.addLayout(version_layout)
        
        # Categoría
        category_layout = QHBoxLayout()
        self.category = QLineEdit()
        self.category.setPlaceholderText("Module Category")
        category_layout.addWidget(QLabel("Category:"))
        category_layout.addWidget(self.category)
        module_layout.addLayout(category_layout)
        
        layout.addWidget(module_info)
        
        # Lista de modelos
        self.models = []
        self.models_layout = QVBoxLayout()
        layout.addLayout(self.models_layout)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        add_model_btn = QPushButton("Add Model")
        generate_btn = QPushButton("Generate Module")
        
        add_model_btn.clicked.connect(self.add_model)
        generate_btn.clicked.connect(self.generate_module)
        
        buttons_layout.addWidget(add_model_btn)
        buttons_layout.addWidget(generate_btn)
        layout.addLayout(buttons_layout)
        
        self.add_model()  # Añadir un modelo inicial

    def add_model(self):
        model = ModelWidget()
        self.models.append(model)
        self.models_layout.addWidget(model)

    def generate_module(self):
        if not self.module_name.text():
            QMessageBox.warning(self, "Error", "Module name is required!")
            return
        
        # Create module directory and basic structure
        module_path = os.path.join(os.getcwd(), self.module_name.text())
        models_path = os.path.join(module_path, 'models')
        security_path = os.path.join(module_path, 'security')
        views_path = os.path.join(module_path, 'views')
        static_path = os.path.join(module_path, 'static', 'description')
        
        # Create all necessary directories
        os.makedirs(models_path, exist_ok=True)
        os.makedirs(security_path, exist_ok=True)
        os.makedirs(views_path, exist_ok=True)
        os.makedirs(static_path, exist_ok=True)
        
        # Generate all components
        self.generate_init(module_path)
        self.generate_manifest(module_path)
        self.generate_models(models_path)
        self.generate_security(security_path)
        self.generate_views(views_path)
        self.generate_menu_views(views_path)
        
        # Create icon placeholder
        icon_path = os.path.join(static_path, 'icon.png')
        open(icon_path, 'a').close()
        
        # Generate bash script
        script_path = self.generate_bash_script()
        
        QMessageBox.information(self, "Success", 
                              f"Module generated successfully at {module_path}\n"
                              f"Bash script generated at {script_path}")

    def generate_manifest(self, module_path):
        manifest = {
            'name': self.module_name.text(),
            'version': self.version.text(),
            'category': self.category.text(),
            'summary': 'Generated by OdooMaster',
            'description': '''
                This module was automatically generated by OdooMaster.
            ''',
            'depends': ['base'],
            'data': [
                'security/ir.model.access.csv',
            ],
            'installable': True,
            'application': True,
        }
        
        with open(os.path.join(module_path, "__manifest__.py"), "w") as f:
            f.write("# -*- coding: utf-8 -*-\n{\n")
            for key, value in manifest.items():
                if isinstance(value, str):
                    f.write(f"    '{key}': '{value}',\n")
                else:
                    f.write(f"    '{key}': {value},\n")
            f.write("}\n")

    def generate_models(self, models_path):
        # Generar __init__.py
        with open(os.path.join(models_path, "__init__.py"), "w") as f:
            for i, model_widget in enumerate(self.models):
                model_name = model_widget.model_name.text().split('.')[-1]
                f.write(f"from . import {model_name}\n")
        
        # Generar archivos de modelo
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if not model_name:
                continue
                
            filename = f"{model_name.split('.')[-1]}.py"
            with open(os.path.join(models_path, filename), "w") as f:
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write("from odoo import models, fields, api\n")
                f.write("from odoo.exceptions import ValidationError\n\n")
                
                f.write(f"class {model_name.replace('.', '_')}(models.Model):\n")
                f.write(f"    _name = '{model_name}'\n")
                f.write(f"    _description = '{model_name} Model'\n\n")
                
                # Generar campos
                for field_widget in model_widget.fields:
                    name = field_widget.name.text()
                    if not name:
                        continue
                        
                    field_type = field_widget.field_type.currentText()
                    string = field_widget.string.text() or name.capitalize()
                    required = field_widget.required.isChecked()
                    
                    f.write(f"    {name} = fields.{field_type}(\n")
                    
                    # Handle Selection field type
                    if field_type == 'Selection':
                        options = []
                        for key, value in field_widget.selection_options:
                            if key.text() and value.text():
                                options.append(f"('{key.text()}', '{value.text()}')")
                        if options:
                            f.write("        selection=[\n")
                            for option in options:
                                f.write(f"            {option},\n")
                            f.write("        ],\n")
                    
                    f.write(f"        string='{string}',\n")
                    if required:
                        f.write("        required=True,\n")
                    f.write("    )\n")
                
                # Add validations after fields
                validations = []
                for field_widget in model_widget.fields:
                    validations.extend(field_widget.get_validation_code())
                
                if validations:
                    f.write("\n    # Validations\n")
                    for validation in validations:
                        f.write(validation)

    def generate_security(self, module_path):
        security_path = os.path.join(module_path, 'security')
        os.makedirs(security_path, exist_ok=True)
        
        with open(os.path.join(security_path, 'ir.model.access.csv'), 'w') as f:
            f.write("id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n")
            for model_widget in self.models:
                model_name = model_widget.model_name.text()
                if not model_name:
                    continue
                model_id = model_name.replace('.', '_')
                f.write(f"access_{model_id},access_{model_id},model_{model_id},,1,1,1,1\n")

    def generate_views(self, module_path):
        views_path = os.path.join(module_path, 'views')
        os.makedirs(views_path, exist_ok=True)
        
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if not model_name:
                continue
            
            view_filename = f"{model_name.split('.')[-1]}_views.xml"
            with open(os.path.join(views_path, view_filename), 'w') as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n')
                
                # Form View
                f.write(f'''    <record id="{model_name}_form" model="ir.ui.view">
        <field name="name">{model_name}.form</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <group>''')
                
                # Primera mitad de los campos
                fields_count = len(model_widget.fields)
                mid_point = fields_count // 2
                
                for field_widget in model_widget.fields[:mid_point]:
                    field_name = field_widget.name.text()
                    if field_name:
                        f.write(f'\n                            <field name="{field_name}"/>')
                
                f.write('''
                        </group>
                        <group>''')
                
                # Segunda mitad de los campos
                for field_widget in model_widget.fields[mid_point:]:
                    field_name = field_widget.name.text()
                    if field_name:
                        f.write(f'\n                            <field name="{field_name}"/>')
                
                f.write('''
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>\n\n''')
                
                # Tree View
                f.write(f'''    <record id="{model_name}_tree" model="ir.ui.view">
        <field name="name">{model_name}.tree</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <tree>''')
                
                for field_widget in model_widget.fields[:6]:  # Primeros 6 campos para la vista tree
                    field_name = field_widget.name.text()
                    if field_name:
                        f.write(f'\n                <field name="{field_name}"/>')
                
                f.write('''
            </tree>
        </field>
    </record>\n\n''')
                
                # Action
                f.write(f'''    <record id="action_{model_name}" model="ir.actions.act_window">
        <field name="name">{model_name.split('.')[-1].replace('_', ' ').title()}</field>
        <field name="res_model">{model_name}</field>
        <field name="view_mode">tree,form</field>
    </record>\n''')
                
                f.write('</odoo>')

    def generate_menu_views(self, module_path):
        with open(os.path.join(module_path, 'views', 'menu_views.xml'), 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n')
            
            # Root menu
            module_name = self.module_name.text()
            menu_title = module_name.replace('_', ' ').title()
            f.write(f'    <menuitem id="{module_name}_menu_root" name="{menu_title}" sequence="10"/>\n\n')
            
            # Submenus for each model
            for i, model_widget in enumerate(self.models, 1):
                model_name = model_widget.model_name.text()
                if not model_name:
                    continue
                
                menu_name = model_name.split('.')[-1].replace('_', ' ').title()
                f.write(f'''    <menuitem 
        id="{model_name}_menu"
        name="{menu_name}"
        parent="{module_name}_menu_root"
        action="action_{model_name}"
        sequence="{i}"/>\n''')
            
            # App menu item
            f.write(f'''\n    <menuitem 
        id="{module_name}_menu_app" 
        name="{menu_title}" 
        action="action_{self.models[0].model_name.text()}"
        sequence="1" 
        web_icon="{module_name},static/description/icon.png"/>\n''')
            
            f.write('</odoo>')

    def generate_bash_script(self):
        module_name = self.module_name.text()
        script_content = f'''#!/bin/bash

# Set the module name and path
MODULE_NAME="{module_name}"
ADDONS_PATH="/opt/odoo17/odoo17-custom-addons"

# Create the module directory and subdirectories
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME"
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME/models"
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME/views"
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME/security"
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME/static/description"

# Create __init__.py
sudo cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/__init__.py"
# -*- coding: utf-8 -*-

from . import models
EOF

# Create __manifest__.py
sudo cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/__manifest__.py"
# -*- coding: utf-8 -*-
{{
    'name': '{self.module_name.text()}',
    'version': '{self.version.text()}',
    'category': '{self.category.text()}',
    'summary': 'Generated by OdooMaster',
    'description': \'''
        This module was automatically generated by OdooMaster.
        Features include:
        - Custom models and views
        - Basic CRUD operations
        - User-friendly interface
    \''',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv','''

        # Add model views dynamically
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if model_name:
                script_content += f"\n        'views/{model_name.split('.')[-1]}_views.xml',"
        
        script_content += "\n        'views/menu_views.xml',\n"
        script_content += '''    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
EOF'''

        # Add models initialization
        script_content += '''
# Create models/__init__.py
sudo cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/models/__init__.py"
# -*- coding: utf-8 -*-
'''
        
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if model_name:
                script_content += f"from . import {model_name.split('.')[-1]}\n"
        
        script_content += "EOF\n"

        # Add security file
        script_content += '''
# Create security/ir.model.access.csv
sudo cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/security/ir.model.access.csv"
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
'''
        
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if model_name:
                model_id = model_name.replace('.', '_')
                script_content += f"access_{model_id},access_{model_id},model_{model_id},,1,1,1,1\n"
        
        script_content += "EOF\n"

        # Add model files and views
        script_content += self._generate_model_files_script()
        script_content += self._generate_view_files_script()
        script_content += self._generate_menu_views_script()

        # Set proper permissions
        script_content += '''
# Set proper permissions
sudo chown -R odoo:odoo "$ADDONS_PATH/$MODULE_NAME"
sudo chmod -R 755 "$ADDONS_PATH/$MODULE_NAME"

echo "Module generated successfully! Please restart Odoo service to load the new module."
'''

        # Save and make executable
        script_path = os.path.join(os.getcwd(), f"create_{module_name}_module.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        return script_path

    def _generate_model_files_script(self):
        script_content = ""
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if not model_name:
                continue
            
            script_content += f'''
# Create model file for {model_name}
sudo cat <<'EOF' > "$ADDONS_PATH/$MODULE_NAME/models/{model_name.split('.')[-1]}.py"
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class {model_name.split('.')[-1].title().replace('_', '')}(models.Model):
    _name = '{model_name}'
    _description = '{model_name.split('.')[-1].replace('_', ' ').title()}'

'''
            
            # Add fields
            for field_widget in model_widget.fields:
                name = field_widget.name.text()
                if name:
                    field_type = field_widget.field_type.currentText()
                    string = field_widget.string.text() or name.capitalize()
                    required = field_widget.required.isChecked()
                    
                    if field_type == 'Selection':
                        script_content += f"    {name} = fields.{field_type}([\n"
                        for key, value in field_widget.selection_options:
                            if key.text() and value.text():
                                script_content += f"        ('{key.text()}', '{value.text()}'),\n"
                        script_content += f"    ], string='{string}'"
                    else:
                        script_content += f"    {name} = fields.{field_type}(string='{string}'"
                    
                    if required:
                        script_content += ", required=True"
                    script_content += ")\n"
            
            # Add validations
            validations = []
            for field_widget in model_widget.fields:
                validations.extend(field_widget.get_validation_code())
            
            if validations:
                script_content += "\n    # Validations\n"
                for validation in validations:
                    script_content += validation
            
            script_content += "EOF\n"
        return script_content

    def _generate_view_files_script(self):
        script_content = ""
        for model_widget in self.models:
            model_name = model_widget.model_name.text()
            if not model_name:
                continue
            
            view_id_prefix = model_name.replace('.', '_')
            model_label = model_name.split('.')[-1].replace('_', ' ').title()
            
            script_content += f'''
# Create view for {model_name}
sudo cat <<'EOF' > "$ADDONS_PATH/$MODULE_NAME/views/{model_name.split('.')[-1]}_views.xml"
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{view_id_prefix}_view_form" model="ir.ui.view">
        <field name="name">{model_name}.form</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <form string="{model_label}">
                <sheet>
                    <group>'''
            
            # Primera mitad de los campos
            fields_count = len(model_widget.fields)
            mid_point = fields_count // 2
            
            for field_widget in model_widget.fields[:mid_point]:
                field_name = field_widget.name.text()
                if field_name:
                    script_content += f'\n                            <field name="{field_name}"/>'
            
            script_content += '''
                    </group>
                    <group>'''
            
            # Segunda mitad de los campos
            for field_widget in model_widget.fields[mid_point:]:
                field_name = field_widget.name.text()
                if field_name:
                    script_content += f'\n                            <field name="{field_name}"/>'
            
            script_content += '''
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="{}_view_tree" model="ir.ui.view">
        <field name="name">{}.tree</field>
        <field name="model">{}</field>
        <field name="arch" type="xml">
            <tree>'''.format(view_id_prefix, model_name, model_name)

            # Campos para la vista tree (limitados a 6)
            for field_widget in model_widget.fields[:6]:
                field_name = field_widget.name.text()
                if field_name:
                    script_content += f'\n                <field name="{field_name}"/>'

            script_content += f'''
            </tree>
        </field>
    </record>

    <record id="action_{model_name}" model="ir.actions.act_window">
        <field name="name">{model_label}</field>
        <field name="res_model">{model_name}</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
EOF
'''
        return script_content

    def _generate_menu_views_script(self):
        module_name = self.module_name.text()
        menu_title = module_name.replace('_', ' ').title()
        
        script_content = f'''
# Create menu views
sudo mkdir -p "$ADDONS_PATH/$MODULE_NAME/views"
sudo cat <<'EOF' > "$ADDONS_PATH/$MODULE_NAME/views/menu_views.xml"
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="{module_name}_menu_root" name="{menu_title}" sequence="10"/>
'''
        
        # Add model menus
        for i, model_widget in enumerate(self.models, 1):
            model_name = model_widget.model_name.text()
            if model_name:
                menu_name = model_name.split('.')[-1].replace('_', ' ').title()
                script_content += f'''    <menuitem 
        id="{model_name}_menu"
        name="{menu_name}"
        parent="{module_name}_menu_root"
        action="action_{model_name}"
        sequence="{i}"/>
'''
        
        # Add app menu
        if self.models:
            first_model = self.models[0].model_name.text()
            script_content += f'''
    <menuitem 
        id="{module_name}_menu_app"
        name="{menu_title}"
        action="action_{first_model}"
        sequence="1"
        web_icon="{module_name},static/description/icon.png"/>
'''
        
        script_content += '''</odoo>
EOF
'''
        return script_content

    def generate_init(self, module_path):
        # Generate main __init__.py
        with open(os.path.join(module_path, "__init__.py"), "w") as f:
            f.write("# -*- coding: utf-8 -*-\n\n")
            f.write("from . import models\n")
        
        # Generate models/__init__.py
        with open(os.path.join(module_path, "models", "__init__.py"), "w") as f:
            for model_widget in self.models:
                model_name = model_widget.model_name.text()
                if model_name:
                    f.write(f"from . import {model_name.split('.')[-1]}\n")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())