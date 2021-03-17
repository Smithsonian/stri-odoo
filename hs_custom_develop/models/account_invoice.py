# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceInherit3(models.Model):
	_inherit = 'account.invoice'

	charfield_project = fields.Char(string="Project ID", compute="compute_project_id")


	@api.depends('partner_id')
	def compute_project_id(self):
		for invoice in self:
			partner = invoice.partner_id
			if partner.customer_type == 'fund':
				invoice.charfield_project = partner.stri_project


	def _create_sequence(self):
		return self.env['ir.sequence'].sudo().create({
			'name': 'STRI Invoices',
			'code': 'stri.account.invoice',
			'prefix': 'INV',
			'padding': '5'
		})


	def change_move_number(self):
		if self.move_id:
			move = self.env['account.move'].sudo().browse(self.move_id.id)
			move.write({
				'name': self.number
			})


	def change_move_ref(self):
		if self.move_id:
			move = self.env['account.move'].sudo().browse(self.move_id.id)
			number = self.number

			if self.move_id.ref:
				reference = self.move_id.ref.split("/")
				move.write({
					'ref': "{}/{}".format(number, reference[1])
				})

	def send_invoice_email(self, template):
		logging.info("TEMPLATE:" + str(template))
		if not self.x_studio_sent_fund_email:
			# move = env.ref('account.invoice')
			template_id = self.env.ref(template)
			template_id.send_mail(self.id, force_send=True)
			self.write({'x_studio_sent_fund_email': True})
		
	""" def send_fund_invoice_email(self):
		if not self.x_studio_sent_fund_email:
			template_id = self.env.ref('account.email_template_invoice_fund')
			template_id.send_mail(self.id, force_send=True)
			self.write({'x_studio_sent_fund_email': True}) """

	@api.multi
	def action_invoice_open(self):
		"""A continuacion se detalla las opciones que realiza este metodo:
		- crear automaticamente un pago a facturas fondo.
		- asignar un secuencial unico a la factura.

		Raises:
			exceptions.ValidationError: [description]

		Returns:
			[type]: [description]
		"""
		action_open = super(AccountInvoiceInherit3, self).action_invoice_open()
		for inv in self:

			if inv.type == 'out_invoice':
				query_filter = [
					('code', '=', 'stri.account.invoice'), 
					('company_id', '=', inv.company_id.id)
				]
				seq = self.env['ir.sequence'].search(query_filter)
				if not seq:
					self._create_sequence()
				sequence = self.env['ir.sequence'].next_by_code('stri.account.invoice')
				if sequence:
					inv.number = sequence
					inv.change_move_number()
					inv.change_move_ref()
					if inv.partner_id.customer_type != 'fund':
						inv.send_invoice_email('account.email_template_edi_invoice')
					# else:
					# 	if inv.type == 'out_refund' and inv.partner_id.customer_type != 'fund':
					# 		inv.send_invoice_email('account.email_template_edi_invoice')
			else:
				if inv.type == 'out_refund':
					if inv.partner_id.customer_type != 'fund':
						inv.send_invoice_email('account.email_template_edi_invoice')

			# if inv.type == 'out_refund':
			# if inv.type != 'out_invoice':
			# 	continue HICE AJUSTE AQUI
			if inv.type not in ('out_invoice','out_refund'):
				continue

			if inv.partner_id.customer_type == 'regular':
				continue

			if inv.amount_total == 0.00:
				continue
			
			if not inv.date_invoice:
				raise exceptions.ValidationError('Invoice Error - '
				'Date invoice field is required.') 

			Payment = self.env['account.payment'].sudo().with_context(
				default_invoice_ids=[(4, inv.id, False)],
				default_amount = inv.amount_total,
				default_payment_date = inv.date_invoice
			)

			filter_config = 'hs_custom_develop.default_journal_strifund'
			config = self.env['ir.config_parameter'].sudo().get_param(filter_config)
			journal = self.env['account.journal'].sudo().sudo(True).browse(int(config))
			payment_method = self.env.ref('account.account_payment_method_manual_in')
			if not payment_method:
				raise exceptions.ValidationError('Account configuration '
				'module - Default journal Strifund is empty.') 

			payment = Payment.create({
				'payment_method_id': payment_method.id,
				'payment_type': 'inbound',
				'partner_type': 'customer',
				'partner_id': inv.partner_id.id,
				'journal_id': journal.id,
				'company_id': inv.company_id.id,
				'currency_id': inv.company_id.currency_id.id,
			})
			payment.action_validate_invoice_payment()

			if inv.partner_id.customer_type == 'fund' and inv.state == 'paid':
				inv.send_invoice_email('account.email_template_invoice_fund')
				
		return action_open

	""" @api.multi
	def action_invoice_paid(self):
		logging.info("ENTRO AL FOR DE INVOICE PAID:")
		action_paid = super(AccountInvoiceInherit3, self).action_invoice_paid()
		for inv in self:
			if inv.type == 'out_invoice' and inv.partner_id.customer_type == 'fund':
				inv.send_fund_invoice_email()
			logging.info("ENTRO AL IF:")
		return action_paid """
