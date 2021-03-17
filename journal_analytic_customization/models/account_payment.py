# -*- coding: utf-8 -*-
"""
Esta clase fue agregada para dar soporte a los pagos ya que el modulo
original no tiene la opcion de agregar las cuentas analiticas a las 
entradas contables cuando un pago es posteado
"""

from odoo import api, fields, models, _


import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
	_inherit="account.payment"


	@api.multi
	def post(self):
		payment = super(AccountPayment, self).post()
		filter_config = 'journal_analytic_customization.payment_analytic_acc'
		config = self.env['ir.config_parameter'].sudo().get_param(filter_config)
		analytic_account = self.env['account.analytic.account'].sudo().browse(int(config))
		for rec in self:
			aml = self.env['account.move.line'].sudo().search([('payment_id', '=', rec.id)])
			line = aml.filtered(lambda l:l.account_id.internal_type in ('payable', 'receivable'))
			if not line.analytic_account_id:
				line.analytic_account_id = analytic_account
		return payment



	def _get_counterpart_move_line_vals(self, invoice=False):
		line = super(AccountPayment, self).\
			_get_counterpart_move_line_vals(invoice=invoice)
		if invoice:
			for inv in invoice:
				aa_id = inv.journal_id.analytic_account_id.id
				line['analytic_account_id'] = aa_id
				break
		return line