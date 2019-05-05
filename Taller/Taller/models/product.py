# -*- coding: utf-8 -*-
from odoo import models, fields, api

class product_category_type(models.Model):
    _name = 'product.category.accion'
    _description = 'accion en categoria productos'

    name = fields.Char(string="Acción", size=50)

class product_pricelist_partner(object):
    _inherit = 'product.pricelist'

    partner_id = fields.Many2one(
        string="Compañia",
        comodel_name="res.partner",
        domain="[('customer', '=', True)]",
        ondelete="cascade",
        help="Selecciona la compañia a la que se aplicará el complemento.")
