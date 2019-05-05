# -*- coding: utf-8 -*-
# © 2019 jhformatic & Pereira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class PurchaseSubscription(models.Model):
    _name = "gestion.electricidad"
    _description = "Gestion electricidad"

    @api.model
    def get_user_company(self):
        """ Get the company of the user """
        return self.env.user.company_id.id

    state = fields.Selection([('draft', 'Nuevo'),
                              ('open', 'Alta'),
                              ('pending', 'Renovar'),
                              ('close', 'Baja'),
                              ('cancel', 'Cancelado')],
                             string='Situación',
                             required=True, copy=False, default='draft')
    date_start = fields.Date(string='Fecha de inicio', default=fields.Date.today, on_change="_compute_year")
    date = fields.Date(string='Fecha de Fin',
                       help="Dos meses antes de esta fecha será puesto como pendiente.")
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency')
    recurring_invoice_line_ids = fields.One2many(
        'gestion.electricidad.line', 'p_subscription_id', string='Invoice Lines', copy=True)
    #    recurring_rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), (
    #        'yearly', 'Year(s)')], string='Recurrency', help="Invoice automatically repeat at specified interval", required=True, default='monthly')
    #    recurring_interval = fields.Integer(
    #        string='Repeat Every', help="Repeat every (Days/Week/Month/Year)", required=True, default=1)
    #    recurring_next_date = fields.Date(string='Date of Next Invoice', default=fields.Date.today,
    #                                      help="The next invoice will be created on this date then the period will be extended.")
    recurring_total = fields.Float(
        compute='_compute_recurring_total', string="Total Comisión", store=True)
    recurring_total_comercial = fields.Float(
        compute='_compute_recurring_total_comercial', string="Total Beneficio Comercial", store=True)
    description = fields.Text()
    user_id = fields.Many2one('res.users', string='Comercial')
    partner_id = fields.Many2one('res.partner', string="Cliente", on_change="_compute_address")
    code = fields.Char(string='CUPS', index=True, default=lambda self: self.env[
                       'ir.sequence'].next_by_code('gestion.electricidad') or 'Nuevo')
    user_id = fields.Many2one('res.users', string="Comercial")
    company_id = fields.Many2one(
        'res.company', string="Company", required="True", default=get_user_company)
    name = fields.Char(string="Contrato", required=True, store=True)
    Contrato = fields.Selection([('electricidad', 'Electricidad'),('gas', 'Gas')], string='Tipo', required=True, default='electricidad')
    Tarifa = fields.Many2one(
        'gestion.electricidad.tarifa', string='Tarifa Seleccionada')
    potencia_1 = fields.Float(string="Potencia 1(Kw)", store=True)
    potencia_2 = fields.Float(string="Potencia 2(Kw)", store=True)
    potencia_3 = fields.Float(string="Potencia 3(Kw)", store=True)
    potencia_4 = fields.Float(string="Potencia 4(Kw)", store=True)
    potencia_5 = fields.Float(string="Potencia 5(Kw)", store=True)
    potencia_6 = fields.Float(string="Potencia 6(Kw)", store=True)
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    city = fields.Char(string='Población')
    zip = fields.Char(string='C.P.')
    state_id = fields.Many2one('res.country.state', string='Provincia', store=True)
    country_id = fields.Many2one('res.country', string='País')
    pendiente = fields.Boolean(string="Contrato pendiente")
    recurring_total_empresa = fields.Float(
        compute='_compute_recurring_total_empresa', string="Total Beneficio Empresa", store=True)

    @api.depends('code', 'partner_id')
    def _get_name(self):
        """ Get the name of the subscription : reference - provider """
        for sub in self:
            sub.name = '%s - %s' % (sub.code,
                                    sub.partner_id.name) if sub.code else sub.partner_id.name

    def _track_subtype(self, init_values):
        """ return the subtype state when found in init_values """
        self.ensure_one()
        if 'state' in init_values:
            return 'gestion_electricidad.subtype_state_change_purchase'
        return super(PurchaseSubscription, self)._track_subtype(init_values)

    @api.depends('recurring_invoice_line_ids')
    def _compute_recurring_total_comercial(self):
        """ Compute the reccuring price of the subscription """
        for sub in self:
            sub.recurring_total_comercial = sum(
                line.price_subtotal_comercial for line in sub.recurring_invoice_line_ids)

    @api.depends('recurring_invoice_line_ids')
    def _compute_recurring_total(self):
        """ Compute the reccuring price of the subscription """
        for sub in self:
            sub.recurring_total = sum(
                line.price_subtotal for line in sub.recurring_invoice_line_ids)

    @api.depends('recurring_invoice_line_ids')
    def _compute_recurring_total_empresa(self):
        """ Compute the reccuring price of the subscription """
        for sub in self:
            sub.recurring_total_empresa = sum(
                line.price_subtotal_empresa for line in sub.recurring_invoice_line_ids)

    @api.model
    def create(self, vals):
        """ Set the reference of the subscription before creation """
        vals['code'] = vals.get('code') or self.env.context.get('default_code') or self.env[
            'ir.sequence'].next_by_code('gestion.electricidad') or 'Nuevo'
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = vals['code']
        return super(PurchaseSubscription, self).create(vals)

    @api.multi
    def name_get(self):
        """ Get the name of the subscription : reference - provider """
        res = []
        for sub in self:
            name = '%s - %s' % (sub.code,
                                sub.partner_id.name) if sub.code else sub.partner_id.name
            res.append((sub.id, '%s' % name))
        return res

    @api.multi
    @api.onchange('date_start')
    def _compute_year(self):
        vals = {}
        """ Calcular fecha 1 año despues """
        inicio = self.date_start
        date = fields.Date.to_string(
            fields.Date.from_string(inicio) + relativedelta(years=1))
        vals['date'] = date
        self.update(vals)

    @api.multi
    @api.onchange('partner_id')
    def _compute_address(self):
        vals = {}
        """ Calcular dirección """
        vals['street'] = self.partner_id.street
        vals['street2'] = self.partner_id.street2
        vals['zip'] = self.partner_id.zip
        vals['city'] = self.partner_id.city
        vals['state_id'] = self.partner_id.state_id.id
        vals['country_id'] = self.partner_id.country_id.id
        self.update(vals)


    @api.model
    def cron_gestion_electricidad(self):
        """ Compute the end of the subscription """
        today = fields.Date.today()
        next_month = fields.Date.to_string(
            fields.Date.from_string(today) + relativedelta(months=2))

        # set to pending if date is in less than a2 month
        domain_pending = [('date', '<', next_month), ('state', '=', 'open')]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.write({'state': 'pending'})

        # set to close if date is passed
        domain_close = [('date', '<', today),
                        ('state', 'in', ['pending', 'open'])]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.write({'state': 'close'})

        return dict(pending=subscriptions_pending.ids, Baja=subscriptions_close.ids)

    @api.multi
    def set_open(self):
        """ Set the subscription status to 'open' """
        return self.write({'state': 'open'})

    @api.multi
    def set_pending(self):
        """ Set the subscription status to 'pending' """
        return self.write({'state': 'pending'})

    @api.multi
    def set_cancel(self):
        """ Set the subscription status to 'cancel' """
        return self.write({'state': 'cancel'})

    @api.multi
    def set_close(self):
        """ Set the subscription status to 'close' """
        return self.write({'state': 'close', 'date': fields.Date.from_string(fields.Date.today())})

#    @api.multi
#    def increment_period(self):
#        """ Get the date of the next occurrence """
#        for account in self:
#            current_date = account.recurring_next_date or self.default_get(
#                ['recurring_next_date'])['recurring_next_date']
#            periods = {'daily': 'days', 'weekly': 'weeks',
#                       'monthly': 'months', 'yearly': 'years'}
#            new_date = fields.Date.from_string(current_date) + relativedelta(
#                **{periods[account.recurring_rule_type]: account.recurring_interval})
#            account.write({'recurring_next_date': new_date})

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Search the name of a partner in the subscription list """
        args = args or []
        domain = ['|', ('code', operator, name), ('name', operator, name)]
        partners = self.env['res.partner'].search(
            [('name', operator, name)], limit=limit)
        if partners:
            domain = ['|'] + domain + [('partner_id', 'in', partners.ids)]
        rec = self.search(domain + args, limit=limit)
        return rec.name_get()


class PurchaseSubscriptionLine(models.Model):
    _name = "gestion.electricidad.line"
    _description = "gestion de electricidad Line"

    p_subscription_id = fields.Many2one(
        'gestion.electricidad', string='Contrato')
    name = fields.Integer(string='Año', size=4, on_change="_compute_user_id")
    quantity = fields.Float(string='Comisión',
                            store=True, help="Introduzca porcentaje comisión propia", default=30)
    #    actual_quantity = fields.Float(help="Quantity actually used", default=0.0)
    buy_quantity = fields.Float(string='Comisión Comercial', help="Introduzca el porcentaje de comisión del comercial", required=False, default=50)
    price_unit = fields.Float(string='Beneficio Suministradora', help="Introduzca el beneficio de la empresa suministradora", required=True)
    #    discount = fields.Float(string='Discount (%)')
    price_subtotal = fields.Float(compute='_compute_price_subtotal',
                                  string='Comisión Total',
                                  store=True)
    price_subtotal_comercial = fields.Float(
        compute='_compute_price_subtotal_comercial',
        string='Beneficio Comercial',
        store=True)
    price_subtotal_empresa = fields.Float(
        compute='_compute_price_subtotal_empresa',
        string='Beneficio Empresa',
        store=True)
    cliente_id = fields.Many2one ('res.partner',string="Cliente", store=True)
    #    user_id = fields.Many2one('res.users',
    #                                 string="Comercial",
    #                                 compute="_compute_get_comercial",
    #                                 store=True)
    user_id = fields.Many2one('res.users', string='Comercial', store="True")

    @api.multi
    @api.onchange('name')
    def _compute_user_id(self):
        vals = {}
        user_id = self.p_subscription_id.user_id.id
        vals['user_id'] = user_id
        cliente_id = self.p_subscription_id.partner_id.id
        vals['cliente_id'] = cliente_id
        self.update(vals)

    #    @api.depends('p_subscription_id')
    #    def _compute_get_comercial(self):
    #        user_id = self.p_subscription_id.user_id.id

#   @api.depends('p_subscription_id')
#   def _compute_get_cliente(self):
#       for line in self:
#           line.cliente_id = line.p_subscription_id.partner_id

#    @api.depends('buy_quantity', 'actual_quantity')
#    def _compute_quantity(self):
#        """ Compute the quantity of item in the line """
#        for line in self:
#            line.quantity = max(line.buy_quantity, line.actual_quantity)
#
#    @api.multi
#    def _set_quantity(self):
#        """ Set the actual quantity of the line """
#        for line in self:
#            line.actual_quantity = line.quantity

    @api.depends('price_unit', 'quantity')
    def _compute_price_subtotal(self):
        """ Compute the subtotal price """
        for line in self:
            line.price_subtotal = (line.quantity / 100.0) * line.price_unit

    @api.depends('price_subtotal', 'buy_quantity')
    def _compute_price_subtotal_comercial(self):
        """ Compute the subtotal price """
        for line in self:
            line.price_subtotal_comercial = (line.buy_quantity / 100.0) * line.price_subtotal

    @api.depends('price_subtotal', 'buy_quantity')
    def _compute_price_subtotal_empresa(self):
        """ Compute the subtotal price """
        for line in self:
            line.price_subtotal_empresa = line.price_subtotal - line.price_subtotal_comercial


class PurchaseSubscriptionTarifa(models.Model):
    _name = "gestion.electricidad.tarifa"
    _description = "Tarifas de gas y electricidad"

    name = fields.Text(string='Tarifa', required=True)
    Contrato = fields.Selection([('electricidad', 'Electricidad'),('gas', 'Gas')], string='Tipo de contrato', required=True, default='electricidad')
