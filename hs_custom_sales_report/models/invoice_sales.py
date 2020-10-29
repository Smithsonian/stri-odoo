# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class InvoiceInherit2(models.Model):
	_inherit = 'account.invoice'

	hs_journal = fields.Char(compute='_compute_journal_id', string='Journal', store=True)

	@api.depends('journal_id') 
	def _compute_journal_id(self):
		for invoice in self:
			invoice.hs_journal = invoice.journal_id.name

class accountPaymentInherit(models.Model):
	_inherit = 'account.payment'

	# diario  = fields.Char(string='Invoice Journal', related='partner_id.invoice_ids.journal_id.name')
	# diario = fields.Char(compute='_compute_journal_name', string='Invoice Journal', store=True)
	diario = fields.Char(string='Invoice Journal', compute='_compute_journal_name', search='_search_journal_name')

	@api.depends('invoice_ids') 
	def _compute_journal_name(self):
		for payment in self:
			if payment.invoice_ids:
				for invoice in payment.invoice_ids:
					payment.diario = invoice.journal_id.name
					break
			else:
				payment.diario = False


	def _search_journal_name(self, operator, value):
		return [('name', operator, value)]


	"""	
	@api.depends('invoice_ids.hs_journal') 
	def _compute_journal_name(self):
		for payment in self:
			payment.diario = payment.invoice_ids.hs_journal
	"""