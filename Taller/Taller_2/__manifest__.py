# -*- coding: utf-8 -*-
{
    'name': "Taller_2",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "alvpercam",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','Taller','account'],

    # always loaded
    'data': [
#         'security/ir.model.access.csv',
        'views/account.xml',
#        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo/demo.xml',
    ],
}
