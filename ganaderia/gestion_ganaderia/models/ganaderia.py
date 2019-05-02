# -*- coding: utf-8 -*-
# © 2019 Pereira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ganaderiagrupos(models.Model):
    _name = "ganaderia.grupo"
    _description = "Grupos de crianza de ganaderia"

    name = fields.Char(string="Nombre del grupo")
    inicio = fields.Date(string="Fecha de inicio")
    fin = fields.Date(string="Fecha de fin")
    animales_ids = fields.One2many(
        string="Animales del grupo",
        comodel_name="ganaderia.grupo.vacas",
        inverse_name="grupo_id",
        domain="[('state', 'NOT', Baja)]",
        help="Selecciona los animales que componen el grupo.")
    gastos_ids = fields.One2many(string="Gastos",
                             comodel_name="ganaderia.grupo.line",
                             inverse_name="grupo_id",
                             help="Ingresa los gastos de explotación sin impuestos.")
    state = fields.Selection([('Activo', 'Activo'), ('Baja', 'Baja')],
                             string='Status',
                             default='Activo',
                             copy="False")
    ingreso_subtotal = fields.Float(compute='_compute_ingreso_subtotal',
                                  string='ingresos')
    gasto_subtotal_comercial = fields.Float(
        compute='_compute_gasto_subtotal',
        string='gastos')
    beneficio = fields.Float(compute='_compute_beneficio', string='beneficio')
    description = fields.Text(string="Observaciones")

    @api.multi
    def set_activo(self):
        """ Set the subscription status to 'open' """
        return self.write({'state': 'Activo'})

    @api.multi
    def set_bajayf(self):
        """ Set the subscription status to 'pending' """
        return self.write({'state': 'Baja'})

    @api.depends('animales_ids')
    def _compute_ingreso_subtotal(self):
        """ Calcula el total de ingresos por venta de animales """
        for sub in self:
            sub.recurring_total = sum(
                line.ingreso for line in sub.animales_ids)

    @api.depends('gastos_ids')
    def _compute_gasto_subtotal(self):
        """ Calcula el total de ingresos por venta de animales """
        for sub in self:
            sub.recurring_total = sum(
                line.gasto for line in sub.animales_ids)

    @api.depends('beneficio','ingreso_subtotal','gasto_subtotal_comercial')
    def _compute_gasto_subtotal(self):
        """ Calcula el total de ingresos por venta de animales """
        beneficio = ingreso_subtotal - gasto_subtotal_comercial

class ganaderiavacas(models.Model):
    _name = "ganaderia.grupo.vacas"
    _description = "Gestión alimentación e incidentes vacas"

    name = fields.Char(string="id vaca")
    nacimiento = fields.Date(string="Nacimiento")
    sexo = fields.Selection(
        string="Situación",
        selection=[
                ('Macho', 'Macho'),
                ('Hembra', 'Hembra')],
                default="Hembra", copy="False")
    state = fields.Selection([
                            ('Crecimiento', 'Crecimiento'),
                            ('Adulto', 'Adulto'),
                            ('Baja', 'Baja')],
                            string='Status',
                            default='Crecimiento', copy="False")
    baja = fields.Date(string="baja")
    madre = fields.Many2one(
        string="Vaca",
        comodel_name="ganaderia.grupo.vacas",
        domain="[('state', '=', Adulto)]",
        ondelete="set null",
        help="Selecciona una vaca.")
    grupo_id = fields.Many2one(
        string="Grupo",
        comodel_name="ganaderia.grupo",
        domain="[('state', '=', Activo)]",
        ondelete="set null",
        help="Sleccione el grupo al que pertenece el animal.")
    ingreso = fields.Float(string="Precio venta")

    @api.multi
    def set_crecimiento(self):
        """ Set the subscription status to 'open' """
        return self.write({'state': 'Crecimiento'})

    @api.multi
    def set_adulto(self):
        """ Set the subscription status to 'pending' """
        return self.write({'state': 'Adulto'})

    @api.multi
    def set_baja(self):
        """ Set the subscription status to 'pending' """
        return self.write({'state': 'Baja'})


class ganaderialine(models.Model):
    _name = "ganaderia.grupo.line"
    _description = "Gestión de incidencias de los animales"

    name = fields.Text(string="Concepto")
    fecha = fields.Date(string="Fecha")
    Observaciones = fields.Text(string="Observaciones")
    grupo_id = fields.Many2one(
        string="Grupo",
        comodel_name="ganaderia.grupo",
        domain="[('state', '=', Activo)]",
        ondelete="set null",
        help="Seleccione el grupo al que pertenece el animal.")
    gasto = fields.Float(
        string="Cuantía gasto",
        compute='_compute_cuantia_subtotal')
    unidades = fields.Float(string="Cuantía gasto")
    pvp = fields.Float(string="PVP/Ud")

    @api.depends('pvp','unidades')
    def _compute_cuantia_subtotal(self):
        """ Compute the subtotal price """
        for line in self:
            line.gasto = line.unidades * line.pvp
