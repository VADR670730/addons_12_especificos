# -*- coding: utf-8 -*-
from odoo import models, fields, api

class partner_pricelist(models.Model):
    _inherit = 'res.partner'

    prices_ids = fields.One2many(string="Precios", comodel_name="product.pricelist.item", inverse_name="partner_id")
    journal_id = fields.Many2one(string="Diario", comodel_name="account.journal", ondelete="cascade", help="Selecciona el diario para numeración.")
