# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date:
#    Version: 0.0.0.0
#
#    Description: Report parser for: l10n_ve_tcv_arcv
#
#
##############################################################################
from report import report_sxw
#~ from datetime import datetime
from osv import fields, osv
#~ from tools.translate import _
#~ import pooler
import decimal_precision as dp
import time
#~ import netsvc


##----------------------------------------------------- parser_l10n_ve_tcv_arcv


class parser_l10n_ve_tcv_arcv(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        context = context or {}
        super(parser_l10n_ve_tcv_arcv, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_address': self._get_address,
            'get_summary': self._get_summary,
            })

    def _get_address(self, address):
        """This address must be a res.partner.address instance"""
        return self.pool.get('res.partner').\
            get_partner_address(self.cr, self.uid, address)

    def _get_summary(self, obj_lines, *args):
        '''
        obj_lines: an obj.line_ids (lines to be totalized)
        args: [string] with csv field names to be totalized

        Use in rml:
        [[ repeatIn(get_summary(o.line_ids, ('fld_1', 'fld_2'..)), 't') ]]
        '''
        totals = {}
        field_list = args[0][0]
        fields = field_list.split(',')
        for key in fields:
            totals[key] = 0
        for line in obj_lines:
            for key in fields:
                totals[key] += line[key]
        return [totals]

report_sxw.report_sxw(
    'report.l10n_ve.tcv.arcv.report',
    'l10n_ve.tcv.arcv',
    'addons/l10n_ve_withholding_islr/report/l10n_ve_tcv_arcv.rml',
    parser=parser_l10n_ve_tcv_arcv,
    header=False
    )


##------------------------------------------------------------ l10n_ve_tcv_arcv


class l10n_ve_tcv_arcv(osv.osv_memory):

    _name = 'l10n_ve.tcv.arcv'

    _description = ''

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    def default_get(self, cr, uid, fields, context=None):
        data = super(l10n_ve_tcv_arcv, self).default_get(
            cr, uid, fields, context)

        obj_per = self.pool.get('account.period')
        period_id = obj_per.find(cr, uid, time.strftime('%Y-%m-%d'))
        if period_id:
            period = obj_per.browse(cr, uid, period_id[0], context=context)
            data.update({
                'fiscalyear_id': period.fiscalyear_id.id,
                })
        return data

    def _clear_lines(self, cr, uid, ids, context):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        unlink_ids = []
        for item in self.browse(cr, uid, ids, context={}):
            for l in item.line_ids:
                unlink_ids.append((2, l.id))
            self.write(
                cr, uid, ids, {'line_ids': unlink_ids,
                               'loaded': False}, context=context)
        return True

    ##--------------------------------------------------------- function fields

    _columns = {
        'name': fields.char(
            'Name', size=64, required=False, readonly=False),
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear', 'Fiscal Year', required=True),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', ondelete='restrict'),
        'loaded': fields.boolean(
            'Loaded'),
        'line_ids': fields.one2many(
            'l10n_ve.tcv.arcv.lines', 'line_id', 'Lines'),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, readonly=True,
            ondelete='restrict'),
        }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company').
        _company_default_get(cr, uid, self._name, context=c),
        'loaded': lambda *a: False,
        }

    _sql_constraints = [
        ]

    ##-------------------------------------------------------------------------

    ##---------------------------------------------------------- public methods

    ##-------------------------------------------------------- buttons (object)

    def button_load(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_wh = self.pool.get('islr.wh.doc')
        for item in self.browse(cr, uid, ids, context={}):
            period_ids = [x.id for x in item.fiscalyear_id.period_ids]
            search_args = [('period_id', 'in', period_ids),
                           ('state', '=', 'done'),
                           ('type', 'in', ('in_invoice', 'in_refund')),
                           ]
            if item.partner_id:
                search_args.append(('partner_id', '=', item.partner_id.id))
            data = {}
            wh_ids = obj_wh.search(
                cr, uid, search_args, order='date_uid')
            for wh in obj_wh.browse(cr, uid, wh_ids, context={}):
                if wh.partner_id.id not in data:
                    data.update({
                        wh.partner_id.id: {
                            'to_print': bool(item.partner_id),
                            'partner_id': wh.partner_id.id,
                            'name': wh.partner_id.name,
                            'wh_qty': 1,
                            'wh_lines': 0,
                            'wh_amount': wh.amount_total_ret,
                            'doc_ids': []
                            }
                        })
                else:
                    data[wh.partner_id.id]['wh_qty'] += 1
                    data[wh.partner_id.id]['wh_amount'] += wh.amount_total_ret
                for doc in wh.concept_ids:
                    doc_data = {
                        'doc_id': doc.id,
                        'islr_wh_doc_id': wh.id,
                        'invoice_id': doc.invoice_id.id,
                        'date': wh.date_uid,
                        'number': doc.invoice_id.supplier_invoice_number,
                        'control': doc.invoice_id.nro_ctrl,
                        'code': doc.islr_rates_id.code,
                        'rate': doc.islr_rates_id.wh_perc,
                        'amount_base': doc.base_amount,
                        'amount_wh': doc.amount,
                        }
                    data[wh.partner_id.id]['doc_ids'].append((0, 0, doc_data))
                    data[wh.partner_id.id]['wh_lines'] += 1
            self._clear_lines(cr, uid, ids, context)
            if data:
                data_list = [x for x in data.values()]
                lines = [(0, 0, x) for x in sorted(
                    data_list, key=lambda k: k['name'])]
                self.write(
                    cr, uid, [item.id], {'line_ids': lines,
                                         'loaded': True}, context=context)
        return True

    def button_all(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_lin = self.pool.get('l10n_ve.tcv.arcv.lines')
        for item in self.browse(cr, uid, ids, context={}):
            line_ids = [x.id for x in item.line_ids]
            obj_lin.write(
                cr, uid, line_ids, {'to_print': True}, context=context)
        return True

    def button_none(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_lin = self.pool.get('l10n_ve.tcv.arcv.lines')
        for item in self.browse(cr, uid, ids, context={}):
            line_ids = [x.id for x in item.line_ids]
            obj_lin.write(
                cr, uid, line_ids, {'to_print': False}, context=context)
        return True

    def button_revert(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_lin = self.pool.get('l10n_ve.tcv.arcv.lines')
        for item in self.browse(cr, uid, ids, context={}):
            for line in item.line_ids:
                obj_lin.write(
                    cr, uid, [line.id], {'to_print': not(line.to_print)},
                    context=context)
        return True

    ##------------------------------------------------------------ on_change...

    def on_change_data(self, cr, uid, ids, fiscalyear_id, partner_id):
        res = {}
        res.update({'loaded': False})
        return {'value': res}

    ##----------------------------------------------------- create write unlink

    ##---------------------------------------------------------------- Workflow

l10n_ve_tcv_arcv()


##------------------------------------------------------ l10n_ve_tcv_arcv_lines


class l10n_ve_tcv_arcv_lines(osv.osv_memory):

    _name = 'l10n_ve.tcv.arcv.lines'

    _description = ''

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    ##--------------------------------------------------------- function fields

    _columns = {
        'line_id': fields.many2one(
            'l10n_ve.tcv.arcv', 'Parent', required=True, ondelete='cascade'),
        'name': fields.char(
            'Name', size=64, required=False, readonly=False),
        'to_print': fields.boolean(
            'Print'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', readonly=True, required=True,
            ondelete='restrict'),
        'wh_qty': fields.integer(
            'Wh qty', readonly=True),
        'wh_lines': fields.integer(
            'Wh lines', readonly=True),
        'wh_amount': fields.float(
            'Wh amount', digits_compute=dp.get_precision('Account'),
            readonly=True),
        'doc_ids': fields.one2many(
            'l10n_ve.tcv.arcv.lines.docs', 'line_id', 'String', readonly=True),
        }

    _defaults = {
        }

    _sql_constraints = [
        ]

    ##-------------------------------------------------------------------------

    ##---------------------------------------------------------- public methods

    ##-------------------------------------------------------- buttons (object)

    ##------------------------------------------------------------ on_change...

    ##----------------------------------------------------- create write unlink

    ##---------------------------------------------------------------- Workflow

l10n_ve_tcv_arcv_lines()


##------------------------------------------------------- l10n_ve_tcv_arcv_docs


class l10n_ve_tcv_arcv_lines_docs(osv.osv_memory):

    _name = 'l10n_ve.tcv.arcv.lines.docs'

    _description = ''

    _order = 'sequence'

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    ##--------------------------------------------------------- function fields

    _columns = {
        'line_id': fields.many2one(
            'l10n_ve.tcv.arcv.lines', 'Parent', required=True,
            ondelete='cascade'),
        'doc_id': fields.many2one(
            'islr.wh.doc.line', 'Doc line', required=True,
            ondelete='restrict'),
        'islr_wh_doc_id': fields.many2one(
            'islr.wh.doc', 'Withhold Document', ondelete='restrict',
            help="Document Retention income tax generated from this bill"),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', help="Withheld invoice"),
        'date': fields.date(
            'Date', required=True, readonly=True),
        'number': fields.char(
            '# Inv', size=64, required=False, readonly=False),
        'control': fields.char(
            '# Control', size=64, required=False, readonly=False),
        'code': fields.char(
            'Code', size=64, required=False, readonly=False),
        'rate': fields.float(
            'Rate', digits_compute=dp.get_precision('Account')),
        'amount_base': fields.float(
            'Base', digits_compute=dp.get_precision('Account')),
        'amount_wh': fields.float(
            'Withholging', digits_compute=dp.get_precision('Account')),

        }

    _defaults = {
        }

    _sql_constraints = [
        ]

    ##-------------------------------------------------------------------------

    ##---------------------------------------------------------- public methods

    ##-------------------------------------------------------- buttons (object)

    ##------------------------------------------------------------ on_change...

    ##----------------------------------------------------- create write unlink

    ##---------------------------------------------------------------- Workflow

l10n_ve_tcv_arcv_lines_docs()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
