# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"

    categ_id = fields.Selection(string="Acción",selection=[('Remolque', 'Remolque'),('Rep in Situ', 'Rep in Situ'),('Suplidos', 'Suplidos'),('Alquiler', 'Alquiler'),],)

class product_pricelist_partner(models.Model):
    _inherit = 'product.pricelist'

    partner_id = fields.Many2one( string="Compañia a aplicar", comodel_name="res.partner", domain="[('customer', '=', True)]", ondelete="cascade")

class product_pricelist_item_partner(models.Model):
    _inherit = 'product.pricelist.item'

    partner_id = fields.Many2one(string="Compañia a aplicar", comodel_name="res.partner", domain="[('customer', '=', True)]", ondelete="cascade")
    product_categ_id = fields.Many2one(string="Acción", comodel_name="product.category", ondelete="cascade")

    @api.multi
    @api.onchange('product_tmpl_id')
    def _compute_user_id(self):
        vals = {}
        partner_id = self.pricelist_id.partner_id.id
        vals['partner_id'] = partner_id
        categ_id = self.product_tmpl_id.categ_id.id
        vals['product_categ_id'] = categ_id
        self.update(vals)
