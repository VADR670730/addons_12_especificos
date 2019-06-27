# -*- coding: utf-8 -*-
from odoo import models, fields, api

class partner_pricelist(models.Model):
    _inherit = 'res.partner'

    prices_ids = fields.One2many(string="Precios", comodel_name="product.pricelist.item", inverse_name="partner_id")
