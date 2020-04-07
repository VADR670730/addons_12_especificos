# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models

class SrpricelistItemQty(models.Model):
    _inherit = 'product.pricelist.item'

    product_uom_qty = fields.Float(string='Cantidad', required=True, default=1.0)


class PricelistItemLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_item_id = fields.Many2one(string="Producto_2", readonly=False, comodel_name="product.pricelist.item", onchange="change_item", store=True)

    @api.multi
    @api.onchange('pricelist_item_id')
    def change_item(self):
        vals = {}
        product_id = self.pricelist_item_id.product_id.id
        vals['product_id'] = product_id
        self.update(vals)

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
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".'
                  ) % (self.product_id.name, self.product_id.id,
                       self.product_id.categ_id.name))

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
            'pricelist_item_id': self.pricelist_item_id.id,
        }
        return res


class SrMultiProduct(models.TransientModel):
    _name = 'sr.multi.product'

    product_ids = fields.Many2many('product.product', string="Product")
    remolque = fields.Many2one(string="Tipo de vehiculo",
                               comodel_name="product.category",
                               ondelete="cascade",
                               help="Selecciona la acción a realizar.")
    categ_id = fields.Selection(
        string="Acción",
        selection=[
            ('Remolque', 'Remolque'),
            ('Rep in Situ', 'Rep in Situ'),
            ('Suplidos', 'Suplidos'),
            ('Alquiler', 'Alquiler'),
        ],
    )
    pricelist_id = fields.Many2one('product.pricelist',
                                   string="Complemento",
                                   default="_default_products")
    prices_ids = fields.Many2many('product.pricelist.item', string="Precios")

    @api.multi
    def add_product(self):
        for line in self.prices_ids:
            self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'order_id': self._context.get('active_id'),
                'pricelist_id': self.pricelist_id.id,
                'product_uom_qty': line.product_uom_qty
            })
        return

    @api.model
    def _prepare_default_get(self, order):
        default = {
            'pricelist_id': order.pricelist_id.id,
            'categ_id': order.categ_id,
            'remolque': order.remolque.id,
        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(SrMultiProduct, self).default_get(fields)
        assert self._context.get('active_model') == 'sale.order',\
            'active_model should be sale.order'
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        default = self._prepare_default_get(order)
        res.update(default)
        return res
'''
    @api.multi
    def _default_products(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', False) or False
        record = self.env['sale.order'].browse(active_id)
        return record.pricelist_id
'''
'''
    @api.multi
    def add_product(self):
        for record in self:
            record.pricelist_id = self.pricelist_id.id,
            record.categ_id = self.categ_id,
            record.remolque = self.remolque.id,
            for line in record.prices_ids:
                self.env['sale.order.line'].create({
                    'product_id': line.product_id.id,
                    'order_id': self._context.get('active_id'),
                    'pricelist_id': self.pricelist_id.id
                })
        return

    @api.model
	def default_get(self):
		ctx = self._context
        if ctx.get('active_model') == 'sale.order':
        return self.env['sale.order'].browse(ctx.get('active_ids')[0]).partner_id.id
'''
