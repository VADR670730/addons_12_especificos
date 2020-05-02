# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice_extra(models.Model):
    _inherit = 'account.invoice'

    telefono = fields.Char(string="Teléfono", size=15, copy="True")
    matricula = fields.Char(string="Matricula", size=15, copy="True")
    total_original = fields.Float(string="Total Servicio Original", copy="True")
    vehiculo = fields.Char(string="Vehiculo", size=40, copy="True")
    referencia = fields.Char(string="Referencia", size=30, copy="True")
    recogido = fields.Char(string="Asistido", size=40, copy="True")
    comentarios = fields.Text(string="Comentarios", copy="True")
    categ_id = fields.Selection(string="Acción", copy="True", selection=[('Remolque', 'Remolque'),('Rep in Situ', 'Rep in Situ'),('Suplidos', 'Suplidos'),('Alquiler', 'Alquiler')])
    remolque = fields.Many2one(string="Tipo de Vehiculo", copy="True", comodel_name="product.category", ondelete="cascade", help="Selecciona la acción a realizar.")
    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True,
                               states={'draft': [('readonly', False)]},
                               index=True,
                               help="Keep empty to use the current date",
                               copy=True)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        result = super(account_invoice_extra, self)._onchange_partner_id()
        if self.partner_id and self.type == 'out_invoice':
            self.journal_id = self.partner_id.journal_id.id
        return result


class account_invoice_line_extra(models.Model):
    _inherit = 'account.invoice.line'

    complemento = fields.Many2one(string="Complemento", copy="True", comodel_name="product.pricelist", ondelete="cascade", store=True)
    price_unit = fields.Float(onchange="compute_pricelist_id")
    quantity = fields.Float(default=0.00)

    @api.multi
    @api.onchange('price_unit')
    def compute_pricelist_id(self):
        vals = {}
        pricelist_id = self.invoice_id.pricelist_id.id
        vals['complemento'] = pricelist_id
        self.update(vals)
