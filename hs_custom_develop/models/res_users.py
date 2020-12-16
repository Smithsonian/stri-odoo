# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
	_inherit = 'res.users'


	@api.model	
	def _auth_oauth_rpc(self, endpoint, access_token):
		_logger.info("Entro en _auth_oauth_rpc:")
		resp = super(ResUsers, self)._auth_oauth_rpc(endpoint, access_token)
		if not resp:
			HEADERS = {
				'Authorization': 'Bearer ' + access_token,
				'Accept':  'application/json',
			}
			resp = requests.get(endpoint, headers=HEADERS).json()
			resp['vso'] = True
			_logger.info("El valor de resp: {}".format(str(resp)))
		return resp
			


	@api.model
	def _auth_oauth_validate(self, provider, access_token):
		_logger.info("Entro en _auth_oauth_validate")
		resp = super(ResUsers, self)._auth_oauth_validate(provider, access_token)
		if resp.get('vso'):
			email = resp.get('email')
			user_id = self.env['res.users'].sudo().search([('login', '=', email))], limit=1)
			if user_id:
				oauth_uid = str(resp.get('user_id'))
				user_id.write({
					'oauth_uid':oauth_uid,
					'oauth_provider_id':provider
				})
		return resp

