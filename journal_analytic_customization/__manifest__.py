# -*- coding: utf-8 -*-
{
    'name': "Account Journal Customization",
    'summary': """ Set Analytic Account in Receivable Journal Entries. """,
    'description': """
        This module helps to set analytic account on receivable accounting entries.
        Account Receivable Analytic Account field added in account journal and it is visible if
        journal type is sale. And that analytic account will be set on receivable journal item.
    """,
    'author': "Aktiv Software",
    'website': "www.aktivsoftware.com",
    'category': 'Accounting',
    'version': '12.0.1.0.0',
    'depends': ['account_reports'],
    'data': [
        'views/account_journal_views.xml',
        'views/res_config_setting.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
