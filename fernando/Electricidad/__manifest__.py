# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Electricidad',
    'summary': "Gestion de contratos de electricidad y gas.",
    'category': 'Purchases',
    'installable': True,
    'application': True,
    'license' : 'AGPL-3',
    'depends': ['base'],
    'data': [
#        'data/purchase_contract_data.xml',
#        'views/res_partner_views.xml',
        'views/purchase_subscription_views.xml',
        'views/purchase_subscription_tarifa_views.xml',
        'security/ir.model.access.csv',
        'views/gestion_electricidad_line_views.xml',
    ],
    'author': 'jhformatic & Pereira',
    'description':
    """
        Este modulo gestiona contratos de electricidad y gas
            - Añade extensión en contactos
            - Depende de:
                - Contactos, Debates, Reglas de acción automaticas, Precisión decimal (Account, Discount)
    """
}
