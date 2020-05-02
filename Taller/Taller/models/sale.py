# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode


class sale_order_extra(models.Model):
    _inherit = 'sale.order'

    telefono = fields.Char(string="Teléfono", size=15)
    vehiculo = fields.Char(string="Vehiculo", size=40)
    referencia = fields.Char(string="Referencia", size=30)
    recogido = fields.Char(string="Asistido", size=40)
    comentarios = fields.Text(string="Comentarios")
    #    categ_id = fields.Many2one(string="Tipo de vehiculo", comodel_name="product.category", domain="[('name', 'like', remolque)]", ondelete="cascade")
    remolque = fields.Many2one(string="Tipo de vehiculo", comodel_name="product.category", ondelete="cascade", help="Selecciona la acción a realizar.")
    categ_id = fields.Selection(string="Acción",
                                selection=[('Remolque', 'Remolque'),('Rep in Situ', 'Rep in Situ'),
                                    ('Suplidos', 'Suplidos'),
                                    ('Alquiler', 'Alquiler'),
                                ],
                                default="Remolque",
                                )
    mes = fields.Char(string="mes", compute="_compute_year")
    date_invoice = fields.Date(string="Fecha de Servicio")

    def _get_time(self):
        my_date = self.date_order
        vals = {}
        """ Calcula mes sale order para establecer secuencia sale order """
        date = fields.Date.to_string(
            fields.Date.from_string(my_date) + relativedelta(days=1))
        vals['date_invoice'] = date
        self.update(vals)

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        t_date= self.date_order
        date = fields.Date.to_string(
            fields.Date.from_string(t_date) + relativedelta(days=1))
        invoice_vals = {
            'name': self.name or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': self.partner_invoice_id.journal_id.id or journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'telefono': self.telefono,
            'vehiculo': self.vehiculo,
            'recogido': self.recogido,
            'comentarios': self.comentarios,
            'categ_id': self.categ_id,
            'remolque': self.remolque.id,
            'total_original': self.amount_total,
            'pricelist_id': self.pricelist_id.id,
            'referencia': self.referencia,
            'matricula': self.client_order_ref,
            'date_invoice': date,
        }
        return invoice_vals

    '''
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if vals.get('client_order_ref') == "abc":
                if 'company_id' in vals:
                    vals['name'] = "a" + self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.orderenero') or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
            else:
                vals['name'] = "mal" + self.env['ir.sequence'].next_by_code(
                    'sale.order') or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(sale_order_extra, self).create(vals)
        return result
'''

class sale_order_line_extra(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(string="Complemento", readonly=False, comodel_name="product.pricelist", store=True)
    price_unit = fields.Float(onchange="compute_pricelist_id")

    @api.multi
    @api.onchange('price_unit')
    def compute_pricelist_id(self):
        vals = {}
        pricelist_id = self.order_id.pricelist_id.id
        vals['pricelist_id'] = pricelist_id
        self.update(vals)
'''
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
            'complemento': self.pricelist_id.id,
        }
        return res
'''
