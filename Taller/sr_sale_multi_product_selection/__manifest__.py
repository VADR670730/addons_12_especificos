# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': "Sale Order Multi Product Selection",
    'version': "12.0.0.1",
    'summary': "Permite añadir varios productos filtrando en base a los campos añadidos en modulo taller",
    'category': 'Sale Management',
    'description': """
        Permite añadir varios productos filtrando en base a los campos añadidos en modulo taller
    """,
    'author': "Alvaro Pereira",
    'website': " ",
    'depends': ['base', 'sale_management', 'product'],
    'data': [
            'security/ir.model.access.csv',
        'views/sale.xml',
        'views/product.xml',
    ],
    'demo': [],
    "license": "AGPL-3",
    'live_test_url': '',
    'installable': True,
    'application': True,
    'auto_install': False,
}
