# -*- coding: utf-8 -*-
{
	'name': "hs_customer_credit_limit",

	'summary': """
		limite de creditos para clientes""",

	'description': """
		limite de creditos para clientes. Se requiere crear el campo credit_limit con studio
	""",

	'author': "HS Consulting",
	'website': "https://www.hconsul.com/",
	'maintainer': 'Luis Dominguez',

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'tools',
	'version': '1.0',
	'license': 'OPL-1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'hs_customer_class_code'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		# 'views/res_partner_views.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		# 'demo/demo.xml',
	],
}