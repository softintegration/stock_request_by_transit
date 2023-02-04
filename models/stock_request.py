# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockRequest(models.Model):
    _inherit = "stock.request"

    @api.model
    def _get_transit_location_id_domain(self):
        return self.env['res.config.settings']._get_transit_location_id_domain()

    through_transit_location = fields.Boolean(string='Through transit location',
                                              states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    transit_location_id = fields.Many2one('stock.location',string='Transit location',
                                          states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                          domain=lambda self:self._get_transit_location_id_domain())


    @api.onchange('through_transit_location')
    def on_change_through_transit_location(self):
        self.transit_location_id = False
        if self.through_transit_location:
            self.transit_location_id = self._get_default_transit_location_id()


    def _get_default_transit_location_id(self):
        self.ensure_one()
        IrDefault = self.env['ir.default'].sudo()
        transit_location_id =  IrDefault.get('res.config.settings', "transit_location_id",
                             company_id=self.company_id.id or self.env.user.company_id.id)
        return transit_location_id


    def _prepare_picking(self):
        res = super(StockRequest, self)._prepare_picking()
        if self.transit_location_id:
            res['location_dest_id'] = self.transit_location_id.id
        return res


    def _check_validate(self):
        super(StockRequest, self)._check_validate()
        for each in self:
            if each.through_transit_location and each.transit_location_id and each.transit_location_id.id == each.location_dest_id.id:
                raise UserError(_("The destination location must be different from the transit location"))
            if each.through_transit_location and each.transit_location_id and each.transit_location_id.id == each.location_id.id:
                raise UserError(_("The source location must be different from the transit location"))


    """@api.multi
    @api.constrains('location_id','location_dest_id','transit_location_id')
    def _check_locations(self):
        to_check_requests = self.env['stock.request']
        for each in self:
            if not each.transit_location_id:
                to_check_requests |= each
        return super(StockRequest, to_check_requests)._check_locations()"""
