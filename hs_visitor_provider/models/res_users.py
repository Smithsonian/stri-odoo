# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, UserError

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
	_inherit = 'res.users'


	def __update_user_provider(self, provider, visitor_data):
		resp = visitor_data
		email = resp.get('email')
		user_id = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
		if user_id:
			oauth_uid = str(resp.get('user_id'))
			user_id.write({
				'oauth_uid':oauth_uid,
				'oauth_provider_id':provider
			})


	@api.model
	def _auth_oauth_rpc(self, endpoint, access_token):
		vso_provider = self.env.ref('hs_visitor_provider.provider_visitor')
		if vso_provider.validation_endpoint == endpoint:
			HEADERS = {
				'Authorization': 'Bearer ' + access_token,
				'Accept':  'application/json',
			}
			resp = requests.get(endpoint, headers=HEADERS).json()
			self.__update_user_provider(vso_provider.id, resp)
			return resp
		else:
			return super(ResUsers, self)._auth_oauth_rpc(endpoint, access_token)


	"""
	@api.model
	def _auth_oauth_validate(self, provider, access_token):
		resp = super(ResUsers, self)._auth_oauth_validate(provider, access_token)
		if resp.get('vso'):
			email = resp.get('email')
			user_id = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
			if user_id:
				oauth_uid = str(resp.get('user_id'))
				user_id.write({
					'oauth_uid':oauth_uid,
					'oauth_provider_id':provider
				})
		return resp
	"""
