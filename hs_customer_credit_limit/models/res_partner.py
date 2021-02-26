# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	credit_limit = fields.Float('Credit Limit', default=0.00)