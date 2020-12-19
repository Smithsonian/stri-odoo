# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions ,_

import logging
_logger = logging.getLogger(__name__)



class AccountInvoiceInherit2(models.Model):
	_inherit = "account.invoice"


	current_user = fields.Many2one(comodel_name='res.users', string="Current User",
		store=False, default=lambda self: self.env.user)


	can_user_payment = fields.Boolean(string="Puede registar pagos", store=False,
		default= lambda self: self._can_user_payment)
	
	"""
	permit_credit_note = fields.Boolean(string="Permitir Nota de Creditos", 
		computed="_compute_permit_credit_note")

	@api.depends('type', 'date_invoice')
	def _compute_permit_credit_note(self):
		for invoice in self:
			if invoice.type == "out_invoice":
				pass
	"""


	
	@api.depends('current_user')
	def _can_user_payment(self):
		count = 0
		departments = self.current_user.departments_ids
		for dept in departments:
			journals = self.env["account.journal"].search([("department_ids", "=", dept.id), ("type", "in", ["cash", "bank"])])
			if journals:
				count = count + 1
		
		if count > 0:
			return True
		else:
			return False


	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line(self):
		"""Controlamos el diario encargado de asignar las cuentas de BCI y
		Administration

		Raises:
			exceptions.Warning: Si no se encontro un diario asignado a la 
			categoria de producto
		"""
		try:
			for invoice_line in self.invoice_line_ids:
				invoice = invoice_line.invoice_id
				if invoice.type in("out_refund", "in_refund"):
					break
				product = invoice_line.product_id
				_logger.info("El producto encontrado es: '" + str(product.name) + "'")
				if str(product.name) != "False":
					filters = [
						('type', '=', 'sale'),
						('department_ids', '=', product.categ_id.id)
					]
					journal = self.sudo().env["account.journal"].search(filters, limit=1)
					_logger.info("El journal encontrado es: " + journal.name)
					self.journal_id = journal
					break
		except Exception as error:
			raise exceptions.Warning("No se encontraron cuentas por cobrar para el \
				producto ingresado.")

				#no account receivable were found for the selected product


class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"


	def change_invoice_journal(self, invoice, product):
		try:
			# invoice = invoice_line.invoice_id
			if invoice.type in("out_refund", "in_refund"):
				return
			# product = invoice_line.product_id
			# _logger.info("El producto encontrado es: '" + str(product.name) + "'")
			if str(product.name) != "False":
				filters = [
					('type', '=', 'sale'),
					('department_ids', '=', product.categ_id.id)
				]
				journal = self.env["account.journal"].sudo().search(filters, limit=1)
				# _logger.info("El journal encontrado es: " + journal.name)
				if journal.id != invoice.journal_id.id:
					invoice.write({'journal_id':journal.id})
		except Exception as __ERROR:
			raise exceptions.Warning("No se encontraron cuentas por cobrar "
				"para el producto ingresado.")


	@api.model
	def create(self, vals):
		# _logger.info("----------------------------------------------------")
		# _logger.info(str(vals))
		if vals.get('product_id') and vals.get('invoice_id'):
			lines = self.env['account.invoice.line'].sudo()
			result = lines.search([('invoice_id', '=', vals.get('invoice_id'))])
			# _logger.info(str(result))
			if len(result) == 1:
				item_id = vals.get('invoice_id')
				invoice = self.env['account.invoice'].sudo().browse(item_id)
				
				item_id = vals.get('product_id')
				product = self.env['product.product'].sudo().browse(item_id)

				self.change_invoice_journal(invoice, product)
		return super(AccountInvoiceLine, self).create(vals)




class AccountPaymentInherit1(models.Model):
	_inherit = "account.payment"

	current_user = fields.Many2one(comodel_name='res.users', string="Current User",
		store=False, default=lambda self: self.env.user)




class AccountJournalInherit1(models.Model):
	_inherit = "account.journal"


	current_user = fields.Many2one(comodel_name='res.users', string="Current User",
		store=False, default=lambda self: self.env.user)


	department_ids = fields.Many2many("product.category",
		"journal_payment_product_categ_rel", "product_category_id",
		"account_journal_id", "Product Category")


	
	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		if self._context.get('search_journal_id'):
			args.append((('department_ids', '=', self._context['search_journal_id'])))
		return super(AccountJournalInherit1, self)._search(args, offset=offset, 
																 limit=limit, 
																 order=order, 
																 count=count, 
																 access_rights_uid=access_rights_uid
															)