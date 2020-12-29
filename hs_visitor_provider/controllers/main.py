# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import functools
import logging

import json

import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import registry as registry_get

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect


_logger = logging.getLogger(__name__)


class CustomVSOSingnin(http.Controller):
    
    @http.route('/auth_oauth/signin', type='http', auth='none')
    # @fragment_to_query_string
    # def login_visitor(self, **kw):
    #     @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(CustomVSOSingnin, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            user = request.env['res.users'].browse(request.uid)
            if user.has_group('base.group_user'):
                if user.partner_id.company_type == 'company':
                    redirect = '/dashboard'
                else:
                    redirect = b'/web?' + request.httprequest.query_string
            else:
                redirect = '/my/home'
            return http.redirect_with_hash(redirect)
        return response
