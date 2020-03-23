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


class PricelistItemLine(models.Model):
    _inherit = 'account.invoice.line'

    pricelist_item_id = fields.Many2one(string="Producto_2",
                                        readonly=False,
                                        comodel_name="product.pricelist.item",
                                        onchange="change_item",
                                        store=True)

    @api.multi
    @api.onchange('pricelist_item_id')
    def change_item(self):
        vals = {}
        product_id = self.pricelist_item_id.product_id.id
        vals['product_id'] = product_id
        self.update(vals)


class MultiProduct(models.TransientModel):
    _name = 'multi.product'

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
            self.env['account.invoice.line'].create({
                'product_id': line.product_id.id,
                'invoice_id': self._context.get('active_id'),
                'complemento': self.pricelist_id.id,
                'name': line.product_id.name,
                'price_unit': line.fixed_price,
                'account_id': line.product_id.property_account_income_id.id
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
        res = super(MultiProduct, self).default_get(fields)
        assert self._context.get('active_model') == 'account.invoice',\
            'active_model should be account.invoice'
        order = self.env['account.invoice'].browse(self._context.get('active_id'))
        default = self._prepare_default_get(order)
        res.update(default)
        return res
