# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class PurchaseInherit(models.Model):
	_inherit="purchase.order"