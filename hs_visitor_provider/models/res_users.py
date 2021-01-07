# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, UserError
from odoo.addons import base
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')

import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
	_inherit = 'res.users'

	# vso_refresh_token = fields.Char('VSO Refresh Token')

	"""     @api.model
	def _vso_generate_signup_values(self, provider, params):
		email = params.get('email')
		return {
			'name': params.get('name', email),
			'login': email,
			'groups_id': [(6,0, [self.env.ref('base.group_user').id])],
			'email': email,
			'oauth_provider_id': provider,
			'oauth_uid': params['user_id'],
			'oauth_access_token': params['access_token'],
			'active': True,
			'vso_refresh_token': params['vso_refresh_token']
		} """

# 	@api.model
# 	def _vso_auth_oauth_signin(self, provider, params):
# 		try:
# 			oauth_uid = params['user_id']
			
# 			users = self.sudo().search([
# 				("oauth_uid", "=", oauth_uid),
# 				('oauth_provider_id', '=', provider)
# 			], limit=1)
# 			if not users:
# 				users = self.sudo().search([
# 					("login", "=", params.get('email'))
# 				], limit=1)
# 				if users:
# 					users.sudo().write({ 
# 						'oauth_uid': params['user_id'],
# 						'oauth_provider_id': provider,
# 					})
# 			if not users:
# 				raise AccessDenied()
# 			assert len(users.ids) == 1
# 			users.sudo().write({
# 				'oauth_access_token': params['access_token'],
# 				'vso_refresh_token': params['vso_refresh_token']})
# 			return users.login
# 		except AccessDenied as access_denied_exception:
# #             raise access_denied_exception
# 			if self._context and self._context.get('no_user_creation'):
# 				return None
# 			# values = self._vso_generate_signup_values(provider, params)
# 			# try:
# 			#     _, login, _ = self.signup(values)
# 			#     return login
# 			# except (UserError):
# 			raise access_denied_exception

# 	@api.model
# 	def vso_auth_oauth(self, provider, params):
# 		access_token = params.get('access_token')
# 		login = self._vso_auth_oauth_signin(provider, params)
# 		if not login:
# 			raise AccessDenied()
# 		return self._cr.dbname, login, access_token
	def __update_user_provider(self, provider, visitor_data, access_token):
		resp = visitor_data
		logging.info("CONTENIDO DE RESP: " + str(resp))
		logging.info("ACCESS TOKEN: " + str(access_token))
		# logging.info(resp + "CONTENIDO DE RESP: ")
		email = resp.get('email')
		user_id = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
		if user_id:
			oauth_uid = str(resp.get('user_id'))
			user_id.sudo().write({
				'oauth_uid':oauth_uid,
				'oauth_provider_id':provider,
				'oauth_access_token':access_token
			})
			logging.info("CONTENIDO DE RESP: " + str(user_id.oauth_access_token))

	@api.model
	def _auth_oauth_rpc(self, endpoint, access_token):
		vso_provider = self.env.ref('hs_visitor_provider.provider_visitor')
		logging.info("CONTENIDO DE ACCESS TOKEN: " + str(access_token))
		logging.info("ID : " + str(vso_provider.id))
		if vso_provider.validation_endpoint == endpoint:
			HEADERS = {
				'Authorization': 'Bearer ' + access_token,
				'Accept':  'application/json',
			}
			resp = requests.get(endpoint, headers=HEADERS).json()
			self.__update_user_provider(vso_provider.id, resp, access_token)
			return resp
		else:
			logging.info("ENTRO AL ELSE")
			logging.info("ENDPOINT ELSE : " + str(endpoint))
			logging.info("ACCESS TOKEN ELSE : " + str(access_token))
			return super(ResUsers, self)._auth_oauth_rpc(endpoint, access_token)
			

	@api.model
	def _auth_oauth_validate(self, provider, access_token):
		""" return the validation data corresponding to the access token """
		oauth_provider = self.env['auth.oauth.provider'].browse(provider)
		logging.info("OAUTH_PROVIDER: " + str(oauth_provider))
		validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token)
		logging.info("VALIDATION: " + str(validation))
		if validation.get("error"):
			raise Exception(validation['error'])
		if oauth_provider.data_endpoint:
			data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
			validation.update(data)
		return validation