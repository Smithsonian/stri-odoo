# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.addons.auth_oauth.controllers.main import OAuthController, fragment_to_query_string
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class VSOController(OAuthController):
	@http.route('/auth_oauth/signin', type='http', auth='none')
	@fragment_to_query_string
	def signin(self, **kw):
		_logger.info("Los parametos devueltos por VSO son")
		_logger.info(kw)
		return super(VSOController, self).signin(**kw)
"""