# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice_extra(models.Model):
    _inherit = 'account.invoice'

    telefono = fields.Char(string="Teléfono", size=15)
    vehiculo = fields.Char(string="Vehiculo", size=40)
    referencia = fields.Char(string="Referencia", size=30)
    recogido = fields.Char(string="Asistido", size=40)
    comentarios = fields.Text(string="Comentarios")
    categ_id = fields.Many2one(string="Tipo de vehiculo",
                               comodel_name="product.category",
                               domain="[('type', '=', remolque)]",
                               ondelete="cascade")
    remolque = fields.Many2one(string="Acción",
                               comodel_name="product.category.accion",
                               ondelete="cascade",
                               help="Selecciona la acción a realizar.")

class account_invoice_line_extra(models.Model):
    _inherit = 'account.invoice.line'

    pricelist_id = fields.Many2one(string="Complemento", readonly=True, comodel_name="product.pricelist", store=True)
    price_unit = fields.Float(onchange="compute_pricelist_id")

    @api.multi
    @api.onchange('price_unit')
    def compute_pricelist_id(self):
        vals = {}
        pricelist_id = self.order_id.pricelist_id.id
        vals['pricelist_id'] = pricelist_id
        self.update(vals)
