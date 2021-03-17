from odoo import api, models, _
from odoo.tools.misc import format_date


class AccountAgedPartner(models.AbstractModel):
    _inherit = 'account.aged.partner'

    filter_analytic = True
    filter_analytic_group = None

    @api.model
    def _get_options(self, previous_options=None):
        if self.filter_analytic and self._name == 'account.aged.receivable':
            self.filter_analytic_accounts = [] if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids else None
            self.filter_analytic_group = [] if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids else None
        if self.filter_partner:
            self.filter_partner_ids = []
            self.filter_partner_categories = []
        options = self._build_options(previous_options)
        # Disable Analytic filter if user has not analytic access rights.
        if not self._name == 'account.aged.receivable':
            options['analytic'] = False
        if self._name == 'account.aged.receivable':
            if self.env.user.id not in self.env.ref('analytic.group_analytic_accounting').users.ids:
                options['analytic'] = False
            if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids:
                options['analytic'] = True
        return options

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js
        widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        # apply date and date_comparison filter
        self._apply_date_filter(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            searchview_dict['analytic_group'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.group'].search([])]
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))
    
        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info
    
    @api.model
    def _get_lines(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        analytic_groups_list = []
        analtic_account_list = []
        # Added below code to apply analytic filter values on Aged receivable report.
        """ Fetched selected analytic accounts and group from options and
            created final list of analytic accounts """
        if self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids:
            analytic_groups_list = [int(group_id) for group_id in options.get('analytic_group')]
            analtic_account_list = [int(account_id) for account_id in options.get('analytic_accounts')]
            if analytic_groups_list:
                analytic_account_ids = self.env['account.analytic.account'].search([('group_id.id', 'in', analytic_groups_list)]).ids
                analtic_account_list = list(set(analtic_account_list) | set(analytic_account_ids))
        # Passed analytic accounts list
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True,analtic_account_ids=analtic_account_list)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 3 + [{'name': self.format_value(sign * v)} for v in [values['direction'], values['4'],
                                                                                                 values['3'], values['2'],
                                                                                                 values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    caret_type = 'account.move'
                    if aml.invoice_id:
                        caret_type = 'account.invoice.in' if aml.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': line_date,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]] +\
                                   [{'name': v} for v in [line['period'] == 6-i and self.format_value(sign * line['amount']) or '' for i in range(7)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 3 + [{'name': self.format_value(sign * v)} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
            }
            lines.append(total_line)
        return lines