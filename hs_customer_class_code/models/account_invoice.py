# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class accountInvoiceInherit2(models.Model):
	_inherit = "account.invoice"


	class_code = fields.Many2one("class.code", "Class Code")
	customer_is_fund = fields.Boolean(string="Is Customer Fund?", compute="_customer_is_fund", default=False)

	@api.depends('partner_id')
	def _customer_is_fund(self):
		self.customer_is_fund = True if self.partner_id.customer_type == 'fund' else False
