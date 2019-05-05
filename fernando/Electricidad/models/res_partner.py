# -*- coding: utf-8 -*-
# © 2019 jhformatic & Pereira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    po_subscription_count = fields.Integer(
        string='Suscripciones', compute='_po_subscription_count')
    dni = fields.Char(string='NIF')

    @api.multi
    def _po_subscription_count(self):
        """ Compute the  number of subscription(s) """
        for partner in self:
            partner.po_subscription_count = self.env[
                'gestion.electricidad'].search_count([('partner_id', "=", partner.id)])

    @api.multi
    def gestion_electricidad_action_res_partner(self):
        """ Action on click on the stat button in partner form """
        for partner in self:
            return {
                "type": "ir.actions.act_window",
                "res_model": "gestion.electricidad",
                "views": [[False, "tree"], [False, "form"]],
                "domain": [["partner_id", "=", partner.id]],
                "context": {"create": False},
                "name": "Purchase Subscriptions",
            }
