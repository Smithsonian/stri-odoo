# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby, formataddr
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
	_inherit="mail.message"


	@api.model
	def _get_default_from(self):
		config_model = self.env['ir.config_parameter'].sudo()
		from_email = config_model.get_param('mail.notification.email')
		if from_email:
			name_email = config_model.get_param('mail.notification.name')
			return formataddr((name_email, from_email)) 
		else:
			return super(MailMessage, self)._get_default_from()
		raise UserError(_("Unable to post message, please configure the sender's email address."))

class AccountFollowupReport(models.AbstractModel):
	_inherit = "account.followup.report"

	@api.model
	def send_email(self, options):
		"""
		Send by mail the followup to the customer
		"""
		partner = self.env['res.partner'].browse(options.get('partner_id'))
		email = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice']).email
		logging.info("VALOR DE PARTNER: " + str(partner))
		logging.info("VALOR DE EMAIL: " + str(email))

		config_ms = self.env['ir.config_parameter'].sudo()
		ms_email = config_ms.get_param('mail.notification.email')
		if email:
			logging.info("VALOR DE MS_MAIL: " + str(ms_email))
			body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang).get_html(options)
			start_index = body_html.find(b'<span>', body_html.find(b'<div class="o_account_reports_summary">'))
			end_index = start_index > -1 and body_html.find(b'</span>', start_index) or -1
			if end_index > -1:
				replaced_msg = body_html[start_index:end_index].replace(b'\n', b'')
				body_html = body_html[:start_index] + replaced_msg + body_html[end_index:]
			msg = _('Follow-up email sent to %s') % email
			# Remove some classes to prevent interactions with messages
			msg += '<br>' + body_html.decode('utf-8')\
				.replace('o_account_reports_summary', '')\
				.replace('o_account_reports_edit_summary_pencil', '')\
				.replace('fa-pencil', '')
			msg_id = partner.message_post(body=msg, message_type='email')
			email = self.env['mail.mail'].create({
				'mail_message_id': msg_id.id,
				'subject': _('%s Payment Reminder') % (self.env.user.company_id.name) + ' - ' + partner.name,
				'body_html': append_content_to_html(body_html, self.env.user.signature or '', plaintext=False),
				'email_from': ms_email,
				'email_to': email,
				'body': msg,
			})
			partner.message_subscribe([partner.id])
		else:
			return super(AccountFollowupReport, self).send_email()
		raise UserError(_('Could not send mail to partner because it does not have any email address defined'))