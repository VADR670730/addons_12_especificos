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

    @api.multi
    def action_invoice_create(self, grouped=True, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id,
                                                  order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice,
                                 precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[
                            group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0
                                               and final):
                    if pending_section:
                        line_vals_list.extend(
                            pending_section.invoice_line_create_vals(
                                invoices[group_key].id,
                                pending_section.qty_to_invoice))
                        pending_section = None
                    line_vals_list.extend(
                        line.invoice_line_create_vals(invoices[group_key].id,
                                                      line.qty_to_invoice))

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({
                'name':
                ', '.join(invoices_name[group_key]),
                'origin':
                ', '.join(invoices_origin[group_key])
            })
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(
                _('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'
                  ))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(
                    _('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'
                      ))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            # Idem for partner
            so_payment_term_id = invoice.payment_term_id.id
            fp_invoice = invoice.fiscal_position_id
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = fp_invoice
            # To keep the payment terms set on the SO
            invoice.payment_term_id = so_payment_term_id
            invoice.message_post_with_view(
                'mail.message_origin_link',
                values={
                    'self': invoice,
                    'origin': references[invoice]
                },
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

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
