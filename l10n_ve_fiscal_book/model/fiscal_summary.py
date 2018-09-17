# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan Márquez
#    Creation Date: 2015-06-18
#    Version: 0.0.0.1
#
#    Description:
#
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from osv import fields, osv
from tools.translate import _
#~ import pooler
import decimal_precision as dp
import time
#~ import netsvc

#~ secuence for summary book format #1
__summary_book_1__ = (
    10000, 10100, 10200, 10300, 10400, 10500, 10600, 10700, 10800, 10900,
    20000, 20100, 20200, 20300, 20400, 20500, 20600, 20700, 20800, 20900,
    21000, 21100, 21200, 21300, 21400, 21500, 21600, 21700, 30000, 30100,
    30200, 30300, 30400, 30450, 30500, 30600, 30700, 30800, 30850, 30900,
    31000, 31100,
    31200, 31300, 31400, 31500, 31600, 31700, 31800, 31900, 32000, 32100,
    32200)


#~ line names for summary book
__summary_book_lines__ = {
    10000: 'DEBITOS FISCALES\tview',
    10100: '[1] VENTAS INTERNAS NO GRAVADAS',
    10200: '[2] VENTAS DE EXPORTACION',
    10300: '[3] VENTAS INTERNAS GRAVADAS POR ALICUOTA GENERAL',
    10400: '[4] VENTAS INTERNAS GRAVADAS POR ALICUOTA GENERAL MAS ADICIONAL',
    10500: '[5] VENTAS INTERNAS GRAVADAS POR ALICUOTA REDUCIDA',
    10600: '[6] TOTAL VENTAS Y DEBITOS FISCALES PARA EFECTOS DE DETERMINACION',
    10700: '[7] AJUSTE A LOS DEBITOS FISCALES DE PERIODOS ANTERIORES',
    10800: '[8] CERTIFICADO DE DEBITOS FISCALES EXONERADOS RECIBIDOS ' +
    'DE ENTES EXONERADOS',
    10900: '[9] TOTAL DEBITOS FISCALES',
    20000: 'CREDITOS FISCALES\tview',
    20100: '[10] COMPRAS NO GRAVADAS Y/O SIN DERECHO A CREDITO FISCAL',
    20200: '[11] IMPORTACION GRAVADA POR ALICUOTA GENERAL',
    20300: '[12] IMPORTACIONES GRAVADAS POR ALICUOTA GENERAL MAS ADICIONAL',
    20400: '[13] IMPORTACIONES GRAVADAS POR ALICUOTA REDUCIDA',
    20500: '[14] COMPRAS INTERNAS GRAVADAS POR ALICUOTA GENERAL',
    20600: '[15] COMPRAS INTERNAS GRAVADAS POR ALICUOTA GENERAL MAS ' +
    'ADICIONAL',
    20700: '[16] COMPRAS INTERNAS GRAVADAS POR ALICUOTA REDUCIDA',
    20800: '[17] TOTAL COMPRAS Y CRÉDITOS FISCALES DEL PERIODO',
    20900: '[18] CRÉDITOS FISCALES TOTALMENTE DEDUCIBLES',
    21000: '[19] CRÉDITOS FISCALES PRODUCTO DE LA APLICACIÓN DE LA PRORRATA',
    21100: '[20] TOTAL CRÉDITOS FISCALES DEDUCIBLES',
    21200: '[21] EXCEDENTE DE CRÉDITOS FISCALES DEL MES ANTERIOR\tlast',
    21300: '[22] REINTEGRO SOLICITADO - SOLO EXPORTADORES',
    21400: '[23] REINTEGRO SOLICITADO - SOLO QUIEN SUMINISTRE BIENES A ' +
    'ENTES EXONERADOS',
    21500: '[24] AJUSTES A LOS CRÉDITOS  DE PERIODOS ANTERIORES',
    21600: '[25] CERTIFICADO DE DEBITOS FISCALES EXONERADOS EMITIDOS POR ' +
    'ENTES EXONERADOS',
    21700: '[26] TOTAL CREDITOS FISCALES',
    30000: 'AUTOLIQUIDACION\tview',
    30100: '[27] TOTAL CUOTA TRIBUTARIA',
    30200: '[28] EXCEDENTE DE CREDITO FISCAL PARA EL MES SIGUIENTE',
    30300: '[29] IMPUESTO PAGADO EN DECLARACION SUSTITUIDA',
    30400: '[30] RETENCIONES DESCONTADAS  EN DECLARACION SUSTITUIDA',
    30450: '[31] RETENCIONES DESCONTADAS EN EXCESO DE PERÍODOS ANTERIORES',
    30500: '[32] PERCEPCIONES DESCONTADAS EN DECLARACION SUSTITUIDA',
    30600: '[33] SUB TOTAL IMPUESTO A PAGAR',
    30700: '[34] RETENCIONES ACUMULADAS POR DESCONTAR\tlast',
    30800: '[35] RETENCIONES DEL PERIODO',
    30850: '[36] RETENCIONES DEJADAS DE DESCONTAR',
    30900: '[37] CREDITOS ADQUIRIDOS POR CESION DE RETENCIONES',
    31000: '[38] RECUPERACION DE RETENCIONES SOLICITADO',
    31100: '[39] TOTAL RETENCIONES',
    31200: '[40] RETENCIONES SOPORTADAS Y DESCONTADAS EN ESTA DECLARACION',
    31300: '[41] SALDO DE RETENCIONES DE IVA NO APLICADO',
    31400: '[42] SUB - TOTAL IMPUESTO A PAGAR',
    31500: '[43] PERCEPCIONES ACUMULADAS EN IMPORTACIONES POR DESCONTAR\tlast',
    31600: '[44] PERCEPCIONES DEL PERIODO',
    31700: '[45] CREDITOS ADQUIRIDOS POR CESION DE PERCEPCIONES',
    31800: '[46] RECUPERACION DE PERCEPCIONES SOLICITADO',
    31900: '[47] TOTAL PERCEPCIONES',
    32000: '[48] PERCEPCIONES EN ADUANAS DESCONTADAS EN ESTA DECLARACION',
    32100: '[49] SALDO DE PERCEPCIONES EN ADUANAS NO APLICADO',
    32200: '[50] TOTAL A PAGAR',
    }

__sale_book_keys__ = (
    10100, 10200, 10300, 10400, 10500, 10700, 30800, 30850
    )

__purchase_book_keys__ = (
    20100, 20200, 20300, 20400, 20500, 20600, 20700, 21500
    )

__summary_total_lines__ = (
    10600, 10900, 20800, 20900, 21000, 21100, 21700, 30100, 30200, 30450,
    30600, 31100, 31200, 31300, 31400, 31900, 32000, 32100, 32200
    )

__prior_sumary_key_relations__ = {
    21200: 30200,
    30700: 31300,
    31500: 32100,
    }

##-------------------------------------------------------------- fiscal_summary


class fiscal_summary(osv.osv):

    _name = 'fiscal.summary'

    _description = ''

    ##-------------------------------------------------------------------------

    def default_get(self, cr, uid, fields, context=None):
        data = super(fiscal_summary, self).default_get(
            cr, uid, fields, context)
        if data.get('date'):
            # ~ obj_per = self.pool.get('account.period')
            dt = datetime.strptime(data['date'], '%Y-%m-%d')
            date_from = (dt - relativedelta(weeks=1))
            date_start = date_from.strftime('%Y-%m-%d')
            date_end = (
                date_from + relativedelta(days=6)).strftime('%Y-%m-%d')

            data.update({'date_start': date_start,
                         'date_end': date_end})
            data.update(
                self._get_fiscal_book_ids(cr, uid, date_start, date_end))
        return data

    def name_get(self, cr, uid, ids, context):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        for item in self.browse(cr, uid, ids, context={}):
            res.append((item.id, '%s' % (item.period_id.name)))
        return res

    ##------------------------------------------------------- _internal methods

    def _get_fiscal_book_ids(self, cr, uid, date_start, date_end):
        res = {}
        if not date_start or not date_end:
            return res
        obj_fb = self.pool.get('fiscal.book')
        # ~ obj_per = self.pool.get('account.period')
        # ~ per_brw = obj_per.browse(cr, uid, period_id, context=None)
        dt = datetime.strptime(date_start, '%Y-%m-%d')
        prior_date = (dt - timedelta(days=1)).strftime('%Y-%m-%d')
        fb_ids = False
        # ~ prior_period_id = obj_per.find(cr, uid, prior_date)[0]
        if prior_date:
            prior_summary_id = self.search(
                cr, uid, [('date_end', '=', prior_date)])
            if prior_summary_id:
                res.update({'prior_summary_id': prior_summary_id[0]})
                prior_summary = self.browse(
                    cr, uid, prior_summary_id[0], context=None)
                fb_ids = obj_fb.search(
                    cr, uid, [('date_start', '=', prior_summary.date_start),
                              ('date_end', '=', prior_summary.date_end)])
            if fb_ids and len(fb_ids) == 2:
                for fb in obj_fb.browse(cr, uid, fb_ids, context=None):
                    if fb.type == 'purchase':
                        res.update({'fb_purchase_id': fb.id})
                    elif fb.type == 'sale':
                        res.update({'fb_sale_id': fb.id})
        return res

    def _clear_lines(self, cr, uid, ids, context):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        unlink_ids = []
        for item in self.browse(cr, uid, ids, context={}):
            for l in item.line_ids:
                unlink_ids.append((2, l.id))
            self.write(cr, uid, ids, {'line_ids': unlink_ids}, context=context)
        return True

    def _get_summary_key_value(self, cr, uid, summary_lines,
                               line_key, context):
        #~ summary_lines is a dict with lines values
        #~ like: {key :{'base': x, 'tax': x}}
        return summary_lines.get(
            line_key, {'amount_base': 0, 'amount_tax': 0})

    def _get_summary_lines(self, cr, uid, sum_brw, context):
        res = {}
        if sum_brw:
            for line in sum_brw.line_ids:
                res.update({line.sequence: {'id': line.id,
                                            'amount_base': line.amount_base,
                                            'amount_tax': line.amount_tax}})
        return res

    def _get_sale_book_key(self, sale_totals, line_key):
        res = {'amount_base': 0,
               'amount_tax': 0}
        if line_key == 10100:
            res['amount_base'] = sale_totals['exe']['base']
            res['amount_tax'] = sale_totals['exe']['tax']
        elif line_key == 10200:
            res['amount_base'] = sale_totals['exp']['base']
            res['amount_tax'] = sale_totals['exp']['tax']
        elif line_key == 10300:
            res['amount_base'] = sale_totals['int']['gen']['base']
            res['amount_tax'] = sale_totals['int']['gen']['tax']
        elif line_key == 10400:
            res['amount_base'] = sale_totals['int']['adi']['base']
            res['amount_tax'] = sale_totals['int']['adi']['tax']
        elif line_key == 10500:
            res['amount_base'] = sale_totals['int']['red']['base']
            res['amount_tax'] = sale_totals['int']['red']['tax']
        #~ Moved by seniat to 30850
        elif line_key == 10700:
            res['amount_base'] = sale_totals['aju']['base']
            res['amount_tax'] = sale_totals['aju']['tax']
        elif line_key == 30800:
            res['amount_base'] = sale_totals['ret']['base']
            res['amount_tax'] = sale_totals['ret']['tax']
        elif line_key == 30850:
            res['amount_base'] = sale_totals['aj2']['base']
            res['amount_tax'] = sale_totals['aj2']['tax']
        return res

    def _get_purchase_book_key(self, purchase_totals, line_key):
        res = {'amount_base': 0,
               'amount_tax': 0}
        if line_key == 20100:
            res['amount_base'] = purchase_totals['exe']['base']
            res['amount_tax'] = purchase_totals['exe']['tax']
        elif line_key == 20200:
            res['amount_base'] = purchase_totals['im']['gen']['base']
            res['amount_tax'] = purchase_totals['im']['gen']['tax']
        elif line_key == 20300:
            res['amount_base'] = purchase_totals['im']['adi']['base']
            res['amount_tax'] = purchase_totals['im']['adi']['tax']
        elif line_key == 20400:
            res['amount_base'] = purchase_totals['im']['red']['base']
            res['amount_tax'] = purchase_totals['im']['red']['tax']
        elif line_key == 20500:
            res['amount_base'] = purchase_totals['do']['gen']['base']
            res['amount_tax'] = purchase_totals['do']['gen']['tax']
        elif line_key == 20600:
            res['amount_base'] = purchase_totals['do']['adi']['base']
            res['amount_tax'] = purchase_totals['do']['adi']['tax']
        elif line_key == 20700:
            res['amount_base'] = purchase_totals['do']['red']['base']
            res['amount_tax'] = purchase_totals['do']['red']['tax']
        elif line_key == 21500:
            res['amount_base'] = purchase_totals['aju']['base']
            res['amount_tax'] = purchase_totals['aju']['tax']
        return res

    def _compute_summary_totals(self, cr, uid, summary_lines, context):

        def sum_lines(summary_lines, keys, amounts=('base', 'tax')):
            data = {'amount_base': 0, 'amount_tax': 0}
            for key in keys:
                if 'base' in amounts:
                    data['amount_base'] += summary_lines[key]['amount_base']
                if 'tax' in amounts:
                    data['amount_tax'] += summary_lines[key]['amount_tax']
            return data

        for key in __summary_total_lines__:
            summary_lines[key].update({'amount_base': 0, 'amount_tax': 0})

        summary_lines[10600].update(sum_lines(
            summary_lines,
            [10100, 10200, 10300, 10400, 10500]))
        summary_lines[10900].update(sum_lines(
            summary_lines,
            [10600, 10700, 10800],
            amounts=('tax')))
        summary_lines[20800].update(sum_lines(
            summary_lines,
            [20100, 20200, 20300, 20400, 20500, 20600, 20700]))
        summary_lines[20900].update(sum_lines(
            summary_lines,
            [20800],
            amounts=('tax')))
        summary_lines[21100].update(sum_lines(
            summary_lines,
            [20900, 21000],
            amounts=('tax')))
        summary_lines[21700].update(sum_lines(
            summary_lines,
            [21100, 21200, 21300, 21400, 21500, 21600],
            amounts=('tax')))
        if summary_lines[10900]['amount_tax'] > \
                summary_lines[21700]['amount_tax']:
            summary_lines[30100]['amount_tax'] = (
                summary_lines[10900]['amount_tax'] -
                summary_lines[21700]['amount_tax'])
        else:
            summary_lines[30200]['amount_tax'] = (
                summary_lines[21700]['amount_tax'] -
                summary_lines[10900]['amount_tax'])
        summary_lines[30600]['amount_tax'] = (
            summary_lines[30100]['amount_tax'] -
            summary_lines[30300]['amount_base'] -
            summary_lines[30400]['amount_base'] +
            summary_lines[30450]['amount_base'] -
            summary_lines[30500]['amount_base'])
        summary_lines[31100].update(sum_lines(
            summary_lines,
            [30700, 30800, 30850, 30900, 31000]))
        if summary_lines[30600]['amount_tax']:
            summary_lines[31200]['amount_tax'] = \
                summary_lines[30600]['amount_tax'] if \
                summary_lines[30600]['amount_tax'] <= \
                summary_lines[31100]['amount_base'] else \
                summary_lines[31100]['amount_base']
        summary_lines[31300]['amount_base'] = (
            summary_lines[31100]['amount_base'] -
            summary_lines[31200]['amount_tax'])
        summary_lines[31400]['amount_tax'] = (
            summary_lines[30600]['amount_tax'] -
            summary_lines[31200]['amount_tax'])
        summary_lines[31900].update(sum_lines(
            summary_lines,
            [31500, 31500, 31600, 31700, 31800]))
        if summary_lines[31400]['amount_tax']:
            summary_lines[32000]['amount_tax'] = \
                summary_lines[31400]['amount_tax'] if \
                summary_lines[31400]['amount_tax'] <= \
                summary_lines[31900]['amount_base'] else \
                summary_lines[31900]['amount_base']
        summary_lines[32100]['amount_base'] = (
            summary_lines[31900]['amount_base'] -
            summary_lines[32000]['amount_tax'])
        summary_lines[32200]['amount_tax'] = (
            summary_lines[31400]['amount_tax'] -
            summary_lines[32000]['amount_tax'])
        return summary_lines

    ##--------------------------------------------------------- function fields

    _rec_name = 'period_id, date_end'

    _order = 'period_id desc'

    _columns = {
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, readonly=True,
            ondelete='restrict'),
        'prior_summary_id': fields.many2one(
            'fiscal.summary', 'Prior summary book', readonly=False,
            required=False, help='Show prior fiscal summary book',
            ondelete='restrict'),
        'date': fields.date(
            'Date dec.', required=True, readonly=True,
            states={'draft': [('readonly', False)]}, select=True,
            help="Date when document was declared to SENIAT"),
        'period_id': fields.many2one(
            'account.period', 'Period', required=False, readonly=True,
            states={'draft': [('readonly', False)]}, ondelete='restrict'),
        'date_start': fields.date(  # Set required in view
            'Date from', readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_end': fields.date(  # Set required in view
            'Date to', readonly=True,
            states={'draft': [('readonly', False)]}),
        'fb_purchase_id': fields.many2one(
            'fiscal.book', 'Fiscal Purchase Book', readonly=True,
            required=False, help='Show Fiscal Purchase Book',
            ondelete='restrict'),
        'fb_sale_id': fields.many2one(
            'fiscal.book', 'Fiscal Sale Book', readonly=True, required=False,
            help='Show Fiscal Sale Book', ondelete='restrict'),
        'line_ids': fields.one2many(
            'fiscal.summary.lines', 'line_id', 'Fiscal summary lines',
            readonly=True, states={'draft': [('readonly', False)]},),
        'move_id': fields.many2one(
            'account.move', 'Accounting entries', ondelete='restrict',
            help="The move of this entry line.", select=True, readonly=False),
        'state': fields.selection(
            [('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')],
            string='State', required=True, readonly=True),
        'narration': fields.text(
            'Notes', readonly=False),
        'number': fields.char(
            'Number', size=64, required=False, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Declaration number"),
        'certificate': fields.char(
            'Certificate', size=64, required=False, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Certificate number"),
        }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company').
        _company_default_get(cr, uid, self._name, context=c),
        }

    _sql_constraints = [
        # ~ ('period_uniq', 'UNIQUE(period_id)', 'The period must be unique!'),
        ]

    ##-------------------------------------------------------------------------

    ##---------------------------------------------------------- public methods

    def get_line_values(self, cr, uid, ids, params, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        line_key = params.get('line_key')
        sum_brw = params.get('sum_brw')
        #~ Get values in sale book
        if line_key in __sale_book_keys__:
            return self._get_sale_book_key(
                params['sale_totals'], line_key)
        #~ Get values in purchase book
        elif line_key in __purchase_book_keys__:
            return self._get_purchase_book_key(
                params['purchase_totals'], line_key)
        #~ Load values from prior summary
        elif line_key in __prior_sumary_key_relations__ and \
                sum_brw.prior_summary_id:
            old_key = __prior_sumary_key_relations__[line_key]
            return self._get_summary_key_value(
                cr, uid, params['old_summary_lines'], old_key, context)
        else:
            return {'amount_base': 0,
                    'amount_tax': 0}

    ##-------------------------------------------------------- buttons (object)

    def button_load(self, cr, uid, ids, context=None):
        obj_fb = self.pool.get('fiscal.book')
        for item in self.browse(cr, uid, ids, context={}):
            self._clear_lines(cr, uid, [item.id], context)
            lines = []
            sale_totals = obj_fb._compute_sale_book_totals(
                cr, uid, item.fb_sale_id, context)
            purchase_totals = obj_fb._compute_purchase_book_totals(
                cr, uid, item.fb_purchase_id, context)
            params = {'sum_brw': item,
                      'sale_totals': sale_totals[0],
                      'purchase_totals': purchase_totals[0],
                      'old_summary_lines': self._get_summary_lines(
                          cr, uid, item.prior_summary_id, context)
                      }
            for key in __summary_book_1__:
                data = {
                    'name': __summary_book_lines__.get(key, ''),
                    'sequence': key,
                    }
                params['line_key'] = key
                data.update(self.get_line_values(
                    cr, uid, ids, params, context))
                lines.append((0, 0, data))
            self.write(cr, uid, [item.id], {'line_ids': lines}, context)
            self.button_compute(cr, uid, ids, context)
        return True

    def button_compute(self, cr, uid, ids, context=None):
        #~ Compute summary totals. Any computed value must be
        #~ added to __summary_total_lines__ tuple
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_lin = self.pool.get('fiscal.summary.lines')
        for item in self.browse(cr, uid, ids, context={}):
            summary_lines = self._get_summary_lines(cr, uid, item, context)
            summary_lines = self._compute_summary_totals(
                cr, uid, summary_lines, context)
            for key in __summary_total_lines__:
                data = summary_lines.get(key)
                id = data.pop('id')
                obj_lin.write(cr, uid, [id], data, context=context)
        return True

    ##------------------------------------------------------------ on_change...

    def on_change_period_id(self, cr, uid, ids, date_start,date_end):
        res = {'fb_purchase_id': 0, 'fb_sale_id': 0}
        if date_start and date_end:
            res.update(self._get_fiscal_book_ids(
                cr, uid, date_start, date_end))
        return {'value': res}

    ##----------------------------------------------------- create write unlink

    def create(self, cr, uid, vals, context=None):
        # ~ if vals.get('period_id'):
            # ~ vals.update(self._get_fiscal_book_ids(cr, uid, vals['period_id']))
        res = super(fiscal_summary, self).create(cr, uid, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # ~ if vals.get('period_id'):
            # ~ vals.update(
                # ~ self._get_fiscal_book_ids(cr, uid, vals['period_id']) or
                # ~ {'fb_purchase_id': 0, 'fb_sale_id': 0})
        res = super(fiscal_summary, self).write(cr, uid, ids, vals, context)
        return res

    ##---------------------------------------------------------------- Workflow

    def button_draft(self, cr, uid, ids, context=None):
        vals = {'state': 'draft'}
        return self.write(cr, uid, ids, vals, context)

    def button_done(self, cr, uid, ids, context=None):
        vals = {'state': 'done'}
        return self.write(cr, uid, ids, vals, context)

    def button_cancel(self, cr, uid, ids, context=None):
        vals = {'state': 'cancel'}
        return self.write(cr, uid, ids, vals, context)

    def test_draft(self, cr, uid, ids, *args):
        return True

    def test_done(self, cr, uid, ids, *args):
        for item in self.browse(cr, uid, ids, context={}):
            if not item.line_ids:
                raise osv.except_osv(
                    _('Error!'),
                    _('You must load some lines'))
            elif len(item.line_ids) != len(__summary_book_lines__):
                raise osv.except_osv(
                    _('Error!'),
                    _('Invalid lines, please reload summary lines'))
            if item.fb_purchase_id and item.fb_purchase_id.state != 'done':
                raise osv.except_osv(
                    _('Error!'),
                    _('You must set "Done" purchases book'))
            if item.fb_sale_id and item.fb_sale_id.state != 'done':
                raise osv.except_osv(
                    _('Error!'),
                    _('You must set "Done" sales book'))
        return True

    def test_cancel(self, cr, uid, ids, *args):
        return True


fiscal_summary()


##-------------------------------------------------------- fiscal_summary_lines


class fiscal_summary_lines(osv.osv):

    _name = 'fiscal.summary.lines'

    _description = ''

    _order = 'sequence'

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    ##--------------------------------------------------------- function fields

    def _compute_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            data = __summary_book_lines__.get(
                item.sequence, '').split('\t')
            if len(data) == 1:
                if item.sequence in __summary_total_lines__:
                    data.append('total')
                else:
                    data.append('value')
            res[item.id] = {
                'name': data[0],
                'type': data[1],
                }
        return res

    ##-------------------------------------------------------------------------

    _columns = {
        'line_id': fields.many2one(
            'fiscal.summary', 'Fiscal summary line', required=True,
            ondelete='cascade'),
        'sequence': fields.integer(
            'Sequence', readonly=True, required=True),
        'name': fields.function(
            _compute_all, method=True, type='string', size=132,
            string='Name', multi='all'),
        'type': fields.function(
            _compute_all, method=True, type='string', size=16,
            string='Type', multi='all'),
        'amount_base': fields.float(
            'Base', digits_compute=dp.get_precision('Account'),
            readonly=False),
        'amount_tax': fields.float(
            'Tax', digits_compute=dp.get_precision('Account'),
            readonly=False),
        }

    _defaults = {
        }

    _sql_constraints = [
        ]

    ##-----------------------------------------------------

    ##----------------------------------------------------- public methods

    ##----------------------------------------------------- buttons (object)

    ##----------------------------------------------------- on_change...

    ##----------------------------------------------------- create write unlink

    ##----------------------------------------------------- Workflow


fiscal_summary_lines()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
