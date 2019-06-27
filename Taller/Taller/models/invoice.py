# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice_extra(models.Model):
    _inherit = 'account.invoice'

    telefono = fields.Char(string="Teléfono", size=15)
    matricula = fields.Char(string="Matricula", size=15)
    total_original = fields.Float(string="Total Servicio Original")
    vehiculo = fields.Char(string="Vehiculo", size=40)
    referencia = fields.Char(string="Referencia", size=30)
    recogido = fields.Char(string="Asistido", size=40)
    comentarios = fields.Text(string="Comentarios")
    categ_id = fields.Selection(string="Acción", selection=[('Remolque', 'Remolque'),('Rep in Situ', 'Rep in Situ'),('Suplidos', 'Suplidos'),('Alquiler', 'Alquiler')])
    remolque = fields.Many2one(string="Tipo de Vehiculo", comodel_name="product.category", ondelete="cascade", help="Selecciona la acción a realizar.")

class account_invoice_line_extra(models.Model):
    _inherit = 'account.invoice.line'

    complemento = fields.Many2one(string="Complemento", comodel_name="product.pricelist", ondelete="cascade", store=True)
'''    price_unit = fields.Float(onchange="compute_pricelist_id")

    @api.multi
    @api.onchange('price_unit')
    def compute_pricelist_id(self):
        vals = {}
        pricelist_id = self.order_id.pricelist_id.id
        vals['complemento'] = pricelist_id
        self.update(vals)  '''
