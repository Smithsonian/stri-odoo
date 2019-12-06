# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)


class accountInvoiceInherit2(models.Model):
	_inherit = "account.invoice"


	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line(self):
		for invoice_line in self.invoice_line_ids:
			product = invoice_line.product_id
			_logger.info(product.name)
			journals = self.inv["account.journal"].search([('type', '=', 'sale')])
			_logger.info(journals.name)
			break


		#self.journal_id = journals





class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"


	@api.multi
	def create(self, values):
		overwrite = super(AccountInvoiceLine, self).create(values)
		_logger.info("value of write is:  " + str(values))
		return overwrite