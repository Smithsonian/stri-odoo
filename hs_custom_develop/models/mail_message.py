# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby, formataddr

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