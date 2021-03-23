# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	payment_analytic_acc = fields.Many2one('account.analytic.account', 
		config_parameter='journal_analytic_customization.payment_analytic_acc')