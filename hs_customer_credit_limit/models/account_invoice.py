# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning


class AccountInvoiceInherit(models.Model):
	_inherit = 'account.invoice'


	@api.multi
	def action_invoice_open(self):
		for invoice in self:
			partner = invoice.partner_id
			if partner.customer_type != "regular":
				continue
			if invoice.type != "out_invoice":
				continue
			if invoice.amount_total != 0 and invoice.partner_id:
				total_amount = invoice.amount_total
				total_due = partner.credit
				credit_limit = partner.credit_limit or 0.00
				if credit_limit == 0.00:
					raise Warning("Customer must have an established credit limit!")
				elif total_due > credit_limit:
					raise Warning("Customer credit limit has been reached!")
				elif (total_due + total_amount) > credit_limit:
					raise Warning("Customer credit limit has been reached!")

				


		return super(AccountInvoiceInherit, self).action_invoice_open()