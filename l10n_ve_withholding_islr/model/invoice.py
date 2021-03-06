# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
#~ from tools import config
#~ import time
#~ import datetime
#~ import netsvc



class account_invoice_line(osv.osv):
    """ It adds a field that determines if a line has been retained or not
    """
    _inherit = "account.invoice.line"
    _columns = {
        'apply_wh': fields.boolean('Withheld',
        help="""Indicates whether a line has been retained or not, to
        accumulate the amount to withhold next month, according to the lines
        that have not been retained."""),
        'concept_id': fields.many2one('islr.wh.concept',
        'Withholding  Concept',
        help="Concept of Income Withholding asociate this rate",
        required=False),
    }
    _defaults = {
        'apply_wh': lambda *a: False,
    }

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False, address_invoice_id=False,
                          currency_id=False, context=None):
        """ Onchange information of the product invoice line
        at once in the line of the bill
        @param product: new product for the invoice line
        @param uom: new measuring unit of product
        @param qty: new quantity for the invoice line
        @param name: new description for the invoice line
        @param type: invoice type
        @param partner_id: partner of the invoice
        @param fposition_id: fiscal position of the invoice
        @param price_unit: new Unit Price for the invoice line
        @param currency_id:
        """
        if context is None:
            context = {}
        data = super(
            account_invoice_line, self).product_id_change(cr, uid, ids,
                                                          product, uom,
                                                          qty, name,
                                                          type, partner_id,
                                                          fposition_id,
                                                          price_unit,
                                                          address_invoice_id,
                                                          currency_id,
                                                          context)
        if product:
            pro = self.pool.get('product.product').browse(
                cr, uid, product, context=context)
            if pro.concept_id:
                data['value'].update({'concept_id':pro.concept_id.id})
        return data

    def create(self, cr, uid, vals, context=None):
        """ Initialilizes the fields wh_xml_id and apply_wh,
        when it comes to a new line
        """
        if context is None:
            context = {}

        if context.get('new_key', False):

            vals.update({'wh_xml_id': False,
                         'apply_wh': False,

                         })

        return super(account_invoice_line, self).create(cr, uid, vals, context=context)


account_invoice_line()


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def action_cancel(self, cr, uid, ids, *args):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj_iwdi = self.pool.get('islr.wh.doc.invoices')
        for item in self.browse(cr, uid, ids, context={}):
            iwdi = obj_iwdi.search(cr, uid, [('invoice_id', '=', item.id)])
            if iwdi:
                raise osv.except_osv(
                    _('Error!'),
                    _('You can not cancel an invoice associated with ' +
                      'retention (ISLR)'))
        return super(account_invoice, self).action_cancel(cr, uid, ids, args)

    def _fnct_get_wh_islr_id(self, cr, uid, ids, name, args, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awil_obj = self.pool.get('islr.wh.doc.line')
        awil_ids = awil_obj.search(cr, uid, [('invoice_id','in',ids)], context=context)

        awil_brws = awil_obj.browse(cr, uid, awil_ids, context=context)
        res = {}.fromkeys(ids,False)
        for i in awil_brws:
            if i.invoice_id:
                res[i.invoice_id.id]=i.islr_wh_doc_id.id or False
        return res

    def _get_inv_from_awil(self, cr, uid, ids, context=None):
        '''
        Returns a list of invoices which are recorded in VAT Withholding Docs
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awil_obj = self.pool.get('islr.wh.doc.invoices')
        awil_brws = awil_obj.browse(cr, uid, ids, context=context)
        return [i.invoice_id.id for i in awil_brws if i.invoice_id]

    _columns = {
        'islr_wh_doc_id': fields.function(_fnct_get_wh_islr_id, method=True,
            type='many2one', relation='islr.wh.doc',
            string='Withhold Document',
            store={
                'islr.wh.doc.invoices':(_get_inv_from_awil, ['invoice_id'], 50),
                }, help="This is the ISLR Withholding Document where this invoice is being withheld"),
        'status': fields.selection([
            ('pro', 'Processed withholding, xml Line generated'),
            ('no_pro', 'Withholding no processed'),
            ('tasa', 'Not exceed the rate,xml Line generated'),
        ], 'Status', readonly=True,
            help=''' * The \'Processed withholding, xml Line generated\' state
            is used when a user is a withhold income is processed.
            * The 'Withholding no processed\' state is when user create a
            invoice and withhold income is no processed.
            * The \'Not exceed the rate,xml Line generated\' state is
            used when user create invoice,a invoice no exceed the
            minimun rate.'''),
    }
    _defaults = {
        'status': lambda *a: "no_pro",
    }
## BEGIN OF REWRITING ISLR

    #~ def copy(self, cr, uid, id, default=None, context=None):
        #~ """ Initialized id by duplicating
        #~ """
        #~ if default is None:
            #~ default = {}
        #~ default = default.copy()
        #~ default.update({'islr_wh_doc_id': False})
#~
        #~ return super(account_invoice, self).copy(cr, uid, id, default, context)

    def check_invoice_type(self, cr, uid, ids, context=None):
        """ This method check if the given invoice record is from a supplier
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_brw = self.browse(cr, uid, ids[0], context=context)
        return inv_brw.type in ('in_invoice', 'in_refund')

    def check_withholdable_concept(self, cr, uid, ids, context=None):
        """ Check if the given invoice record is ISLR Withholdable
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        return iwdi_obj._get_concepts(cr, uid, ids, context=context)

    def _create_doc_invoices(self, cr, uid, ids, islr_wh_doc_id,
                             context=None):
        """ This method link the invoices to be withheld
        with the withholding document.
        """
        # TODO: CHECK IF THIS METHOD SHOULD BE HERE OR IN THE ISLR WH DOC
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        iwhdi_ids = []
        for inv_id in ids:
            iwhdi_ids.append(doc_inv_obj.create(cr, uid,
                                                {'invoice_id': inv_id, 'islr_wh_doc_id': islr_wh_doc_id}))
        return iwhdi_ids

    def _create_islr_wh_doc(self, cr, uid, ids, context=None):
        '''Keep to avoid server action problem (original declaration)'''
        return self.create_islr_wh_doc(cr, uid, ids, context)

    def create_islr_wh_doc(self, cr, uid, ids, context=None):
        """ Function to create in the model islr_wh_doc
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        #~ doc_line_obj = self.pool.get('islr.wh.doc.line')
        wh_doc_obj = self.pool.get('islr.wh.doc')
        #~ inv_obj = self.pool.get('account.invoice.line')
        #~ rate_obj = self.pool.get('islr.rates')
        obj_per = self.pool.get('account.period')

        row = self.browse(cr, uid, ids[0], context=context)
        context['type'] = row.type
        wh_ret_code = wh_doc_obj.retencion_seq_get(cr, uid)

        if wh_ret_code:
            per_id = obj_per.find(cr, uid, row.date_invoice)
            islr_wh_doc_id = wh_doc_obj.create(cr, uid,
                                               {'name': _('WH ISLR - ORIGIN %s'%(row.number)),
                                                'partner_id': row.partner_id.id,
                                                'period_id': per_id and per_id[0] or row.period_id.id,
                                                'account_id': row.account_id.id,
                                                'type': row.type,
                                                'journal_id': wh_doc_obj._get_journal(cr, uid, context=context),
                                                'date_ret': row.date_invoice,
                                                'date_uid': row.date_invoice,
                                                })
            self._create_doc_invoices(cr, uid, row.id, islr_wh_doc_id)

            self.pool.get('islr.wh.doc').compute_amount_wh(cr, uid,
                                                           [islr_wh_doc_id],
                                                           context=context)
            if row.company_id.automatic_income_wh is True:
                wh_doc_obj.write(cr, uid, islr_wh_doc_id,
                                 {'automatic_income_wh': True},
                                 context=context)
        else:
            raise osv.except_osv(_('Invalid action !'), _(
                "No se ha encontrado el numero de secuencia!"))

        self.write(cr, uid, ids, {'islr_wh_doc_id': islr_wh_doc_id,
                                  'islr_wh_doc_name': wh_ret_code})

        # wf_service = netsvc.LocalService("workflow")
        # wf_service.trg_validate(uid, 'islr.wh.doc', islr_wh_doc_id,
        # 'button_confirm', cr)
        return islr_wh_doc_id

    def copy(self, cr, uid, id, default=None, context=None):
        """ Inicializes the fields islr_wh_doc and status
        when the line is duplicated
        """
        default = default or {}
        context = context or {}

        default = default.copy()
        default.update({'islr_wh_doc': 0,
                        'status': 'no_pro',
                        })

        context.update({'new_key': True})

        return super(account_invoice, self).copy(cr, uid, id, default,
                                                 context)

    def _refund_cleanup_lines(self, cr, uid, lines):
        """ Initializes the fields of the lines of a refund invoice
        """
        data = super(account_invoice, self)._refund_cleanup_lines(
            cr, uid, lines)
        list = []
        for x, y, res in data:
            if 'concept_id' in res:
                res['concept_id'] = res.get(
                    'concept_id', False) and res['concept_id']
            if 'apply_wh' in res:
                res['apply_wh'] = False
            if 'wh_xml_id' in res:
                res['wh_xml_id'] = 0
            list.append((x, y, res))
        return list

    def validate_wh_income_done(self, cr, uid, ids, context=None):
        """ Method that check if wh income is validated in invoice refund.
        @params: ids: list of invoices.
        return: True: the wh income is validated.
                False: the wh income is not validated.
        """
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund') \
                    and not inv.islr_wh_doc_id:
                rislr = True
            else:
                rislr = not inv.islr_wh_doc_id and True or \
                    inv.islr_wh_doc_id.state in (
                        'done') and True or False
                if not rislr:
                    raise osv.except_osv(
                        _('Error !'),
                        _('The Document you are trying to refund has a ' +
                          'income withholding "%s" which is not yet ' +
                          'validated!' % inv.islr_wh_doc_id.code))
                    return False
        return True

    def _get_move_lines(self, cr, uid, ids, to_wh, period_id, pay_journal_id,
                        writeoff_acc_id, writeoff_period_id, writeoff_journal_id, date,
                        name, context=None):
        """ Generate move lines in corresponding account
        @param to_wh: whether or not withheld
        @param period_id: Period
        @param pay_journal_id: pay journal of the invoice
        @param writeoff_acc_id: account where canceled
        @param writeoff_period_id: period where canceled
        @param writeoff_journal_id: journal where canceled
        @param date: current date
        @param name: description
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(account_invoice, self)._get_move_lines(cr, uid, ids, to_wh,
                                                           period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id,
                                                           writeoff_journal_id, date, name, context=context)

        if not context.get('income_wh', False):
            return res

        inv_brw = self.browse(cr, uid, ids[0])

        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1,
                 'in_refund': -1}
        direction = types[inv_brw.type]

        for iwdl_brw in to_wh:
            if inv_brw.type in ('out_invoice', 'out_refund'):
                acc = iwdl_brw.concept_id.property_retencion_islr_receivable and \
                    iwdl_brw.concept_id.property_retencion_islr_receivable.id or \
                    False
            else:
                acc = iwdl_brw.concept_id.property_retencion_islr_payable and \
                    iwdl_brw.concept_id.property_retencion_islr_payable.id or False
            if not acc:
                raise osv.except_osv(_('Missing Account in Tax!'),
                                     _("Tax [%s] has missing account. "
                                       "Please, fill the missing fields"
                                       ) % (iwdl_brw.concept_id.name,))
            res.append((0, 0, {
                'debit': direction * iwdl_brw.amount < 0 and - direction *
                iwdl_brw.amount,
                'credit': direction * iwdl_brw.amount > 0 and direction *
                iwdl_brw.amount,
                'account_id': acc,
                'partner_id': inv_brw.partner_id.id,
                'ref': inv_brw.number,
                'date': date,
                'currency_id': False,
                'name': _('%s - ISLR: %s') % (name,
                                              iwdl_brw.islr_rates_id.code)
            }))

        return res

    def adjust_wh_islr_doc(self, cr, uid, ids, context):
        if not ids: return {}
        res = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        so_brw = self.browse(cr,uid,ids,context={})[0]
        if so_brw.islr_wh_doc_id and so_brw.islr_wh_doc_id.state != 'draft':
            raise osv.except_osv(_('Error!'),_('Can\'t change withholding concepts when withholding document state\'s <> "draft"'))
        res.update({
            'name': _('Adjust withholding concepts'),
            'type': 'ir.actions.act_window',
            'res_model': 'adjust.wh.islr.doc',
            'view_type': 'form',
            'view_id': False,
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'domain': "",
            'context': {'default_invoice_id':ids[0],
                        }
            })
        return res


account_invoice()
