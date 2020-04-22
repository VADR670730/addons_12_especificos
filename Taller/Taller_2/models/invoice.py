# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice_extra(models.Model):
    _inherit = 'account.invoice'

    telefono = fields.Char(copy="True")
    number = fields.Char(related='move_id.name', store=True, readonly=False, copy=False)
    matricula = fields.Char(copy="True")
    total_original = fields.Float(copy="True")
    vehiculo = fields.Char(copy="True")
    referencia = fields.Char(copy="True")
    recogido = fields.Char(copy="True")
    comentarios = fields.Text(copy="True")
    categ_id = fields.Selection(copy="True")
    remolque = fields.Many2one(copy="True")
    rectificada = fields.Boolean(string="No aprobada", help="Ha tenido que emitirse rectificativa", copy="False")
'''

Seria inter

    @api.model
    def _prepare_refund(self,
                        invoice,
                        date_invoice=None,
                        date=None,
                        description=None,
                        journal_id=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(
            invoice.invoice_line_ids)

        tax_lines = invoice.tax_line_ids
        taxes_to_change = {
            line.tax_id.id: line.tax_id.refund_account_id.id
            for line in tax_lines.filtered(lambda l: l.tax_id.refund_account_id
                                           != l.tax_id.account_id)
        }
        cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
        values['tax_line_ids'] = self._refund_tax_lines_account_change(
            cleaned_tax_lines, taxes_to_change)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search(
                [('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(
            invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['refund_invoice_id'] = invoice.id

        if values['type'] == 'in_refund':
            partner_bank_result = self._get_partner_bank_id(
                values['company_id'])
            if partner_bank_result:
                values['partner_bank_id'] = partner_bank_result.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

'''
