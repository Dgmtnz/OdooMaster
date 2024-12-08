#!/bin/bash

# Update the system
apt-get update -y && apt-get upgrade -y

# Install Python and required libraries
apt-get install -y python3-pip python3-dev python3-venv libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev libffi-dev libmysqlclient-dev libjpeg-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev

# Install NPM and CSS plugins
apt-get install -y npm
ln -s /usr/bin/nodejs /usr/bin/node
npm install -g less less-plugin-clean-css
apt-get install -y node-less

# Install Wkhtmltopdf
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb
apt install -f

# Install PostgreSQL
apt-get install postgresql -y
systemctl start postgresql && systemctl enable postgresql

# Create Odoo and PostgreSQL users
useradd -m -U -r -d /opt/odoo17 -s /bin/bash odoo17
passwd odoo17
su - postgres -c "createuser -s odoo17"

# Install and configure Odoo 17
su - odoo17 << EOF
git clone https://www.github.com/odoo/odoo --depth 1 --branch 17.0 /opt/odoo17/odoo17
cd /opt/odoo17
python3 -m venv odoo17-venv
source odoo17-venv/bin/activate
pip install --upgrade pip
pip3 install wheel
pip3 install -r odoo17/requirements.txt
deactivate
mkdir /opt/odoo17/odoo17-custom-addons
chown -R odoo17:odoo17 /opt/odoo17/odoo17-custom-addons
EOF

mkdir -p /var/log/odoo17
touch /var/log/odoo17.log
chown -R odoo17:odoo17 /var/log/odoo17

# Create Odoo configuration file
cat <<EOF > /etc/odoo17.conf
[options]
admin_passwd = YourStrongPasswordHere
db_host = False
db_port = False
db_user = odoo17
db_password = False
xmlrpc_port = 8069
logfile = /var/log/odoo17/odoo17.log
addons_path = /opt/odoo17/odoo17/addons,/opt/odoo17/odoo17-custom-addons
EOF

# Create Odoo systemd unit file
cat <<EOF > /etc/systemd/system/odoo17.service
[Unit]
Description=odoo17
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo17
PermissionsStartOnly=true
User=odoo17
Group=odoo17
ExecStart=/opt/odoo17/odoo17-venv/bin/python3 /opt/odoo17/odoo17/odoo-bin -c /etc/odoo17.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Odoo service
systemctl daemon-reload
systemctl start odoo17 && systemctl enable odoo17

#!/bin/bash

# Set the module name and path
MODULE_NAME="real_estate_investment"
ADDONS_PATH="/opt/odoo17/odoo17-custom-addons"

# Create the module directory
mkdir -p "$ADDONS_PATH/$MODULE_NAME"

# Create the __init__.py file
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/__init__.py"
# -*- coding: utf-8 -*-

from . import models
EOF

# Create the __manifest__.py file
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/__manifest__.py"
# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Investment',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate investments',
    'description': '''
        This module allows you to manage real estate investments.
        Features include:
        - Property management
        - Investment tracking
        - Financial analysis
    ''',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/property_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
EOF

# Create the models directory and __init__.py file
mkdir -p "$ADDONS_PATH/$MODULE_NAME/models"
touch "$ADDONS_PATH/$MODULE_NAME/models/__init__.py"

# Create the property model file
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/models/property.py"
# -*- coding: utf-8 -*-

from odoo import models, fields

class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True)
    description = fields.Text(string='Description')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('land', 'Land'),
        ('commercial', 'Commercial')
    ], string='Property Type', default='apartment')
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip_code = fields.Char(string='Zip Code')
    country = fields.Char(string='Country')
    purchase_price = fields.Float(string='Purchase Price')
    current_value = fields.Float(string='Current Value')
EOF

# Update the models/__init__.py file
echo "from . import property" >> "$ADDONS_PATH/$MODULE_NAME/models/__init__.py"

# Create the security directory and access rights file
mkdir -p "$ADDONS_PATH/$MODULE_NAME/security"
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/security/ir.model.access.csv"
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_real_estate_property,access_real_estate_property,model_real_estate_property,,1,1,1,1
EOF

# Create the views directory and property views file
mkdir -p "$ADDONS_PATH/$MODULE_NAME/views"
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/views/property_views.xml"
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="real_estate_property_view_form" model="ir.ui.view">
        <field name="name">real.estate.property.form</field>
        <field name="model">real.estate.property</field>
        <field name="arch" type="xml">
            <form string="Real Estate Property">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="description"/>
                        <field name="property_type"/>
                        <field name="address"/>
                        <field name="city"/>
                        <field name="state"/>
                        <field name="zip_code"/>
                        <field name="country"/>
                        <field name="purchase_price"/>
                        <field name="current_value"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="real_estate_property_view_tree" model="ir.ui.view">
        <field name="name">real.estate.property.tree</field>
        <field name="model">real.estate.property</field>
        <field name="arch" type="xml">
            <tree string="Real Estate Properties">
                <field name="name"/>
                <field name="property_type"/>
                <field name="city"/>
                <field name="state"/>
                <field name="country"/>
            </tree>
        </field>
    </record>

    <record id="real_estate_property_action" model="ir.actions.act_window">
        <field name="name">Real Estate Properties</field>
        <field name="res_model">real.estate.property</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
EOF

# Create the menu views file
cat <<EOF > "$ADDONS_PATH/$MODULE_NAME/views/menu_views.xml"
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="real_estate_menu_root" name="Real Estate" sequence="10"/>

    <menuitem id="real_estate_property_menu" name="Properties" parent="real_estate_menu_root" action="real_estate_property_action" sequence="1"/>

    <menuitem id="real_estate_menu_app" name="Real Estate" action="real_estate_property_action" sequence="1" web_icon="real_estate_investment,static/description/icon.png"/>
</odoo>
EOF

# Create the static/description directory and icon file
mkdir -p "$ADDONS_PATH/$MODULE_NAME/static/description"
touch "$ADDONS_PATH/$MODULE_NAME/static/description/icon.png"

echo "Real Estate Investment module created successfully with app menu item!"
