#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
import decimal_precision as dp


class adjust_wh_islr_doc(osv.osv_memory):

    _name = 'adjust.wh.islr.doc'

    _columns = {'name': fields.char('Name', size=64, required=False, readonly=False),
                'invoice_id': fields.many2one('account.invoice', 'Invoice Reference',readonly=True),
                'line_ids':fields.one2many('adjust.wh.islr.doc.line','line_id','Lines'),
                'sure':fields.boolean('Are you sure?'),
        }

    _defaults = {
        'sure': False,
        }

    def default_get(self, cr, uid, fields, context=None):
        data = super(adjust_wh_islr_doc, self).default_get(cr, uid, fields, context)
        if data.get('invoice_id'):
            obj_inv = self.pool.get('account.invoice')
            inv = obj_inv.browse(cr,uid,data['invoice_id'],context=context)
            lines = []
            for l in inv.invoice_line:
                lines.append({'invoice_line_id':l.id,
                              'name':l.name,
                              'concept_id':l.concept_id.id,
                              'amount':l.price_subtotal,
                              'act_concept_id':l.concept_id.id,
                              'new_concept_id':l.concept_id.id})
            if lines:
                data.update({'line_ids':lines})
        return data


    def adjust_wh_concep(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        so_brw = self.browse(cr,uid,ids,context={})[0]
        obj_lin = self.pool.get('account.invoice.line')
        if not so_brw.sure:
            raise osv.except_osv(_("Error!"), _("Please confirm that you know what you're doing by checking the option bellow!"))
        changes = []
        for l in so_brw.line_ids:
            if l.invoice_line_id.id and l.act_concept_id.id != l.new_concept_id.id:
                changes.append({'invoice_line_id':l.invoice_line_id.id,'concept_id':l.new_concept_id.id, 'withholdable_islr':l.new_concept_id.withholdable})
        if not changes:
            raise osv.except_osv(_("Error!"), _("No changes to withholding concept to do!"))
        for c in changes:
            obj_lin.write(cr,uid,c['invoice_line_id'],c,context=context)
            if so_brw.invoice_id:
                if so_brw.invoice_id.islr_wh_doc_id:
                    if c['withholdable_islr']:
                        ## Update withholding amount
                        obj_wh = self.pool.get('islr.wh.doc')
                        obj_wh.compute_amount_wh(cr, uid, [so_brw.invoice_id.islr_wh_doc_id.id], context)
                    else:
                        ## Unlink invoice, withholdable = False
                        obj_wh_inv = self.pool.get('islr.wh.doc.invoices')
                        unlink_ids = obj_wh_inv.search(cr, uid, [('invoice_id', '=', so_brw.invoice_id.id)])
                        if unlink_ids:
                            obj_wh_inv.unlink(cr, uid, unlink_ids,context)
                else:
                    obj_inv = self.pool.get('account.invoice')
                    islr_wh_doc_id = obj_inv.create_islr_wh_doc(cr, uid, [so_brw.invoice_id.id], context)
        return {'type': 'ir.actions.act_window_close'}


adjust_wh_islr_doc()


class adjust_wh_islr_doc_line(osv.osv_memory):

    _name = 'adjust.wh.islr.doc.line'

    _description = "Wizard that changes the withholding concept in invoice lines"

    _columns = {
        'line_id':fields.many2one('adjust.wh.islr.doc', 'Adjust', readonly=True),
        'invoice_line_id': fields.many2one('account.invoice.line', 'line', readonly=False, required=True),
        'name':fields.related('invoice_line_id','name', type='char', size=256, relation='account.invoice.line',
                              string='Description', readonly=True),
        'concept_id': fields.related('invoice_line_id','concept_id', type='many2one', relation='islr.wh.concept',
                                     string='Actual wh concept', readonly=True),
        'amount': fields.related('invoice_line_id','price_subtotal', type='float', relation='account.invoice.line',
                                 string='Amount', readonly=True),
        'act_concept_id': fields.many2one('islr.wh.concept','Act Withholding Concept',
                        help="New concept of Income Withholding asociate this rate"),
        'new_concept_id': fields.many2one('islr.wh.concept','New Withholding Concept', required=True,
                        help="New concept of Income Withholding asociate this rate"),
        }


    #~ def create(self, cr, uid, vals, context=None):
        #~ context = context or {}
        #~ if not context.get('adjust_wh_islr_doc'):
            #~ raise osv.except_osv(_('Error!'),_('Can\'t add more lines.'))
        #~ res = super(adjust_wh_islr_doc, self).create(cr, uid, vals, context)
        #~ return res
        #~
    #~ def unlink(self, cr, uid, vals, context=None):
        #~ context = context or {}
        #~ if not context.get('adjust_wh_islr_doc'):
            #~ raise osv.except_osv(_('Error!'),_('Can\'t delete lines.'))
        #~ res = super(adjust_wh_islr_doc, self).unlink(cr, uid, vals, context)
        #~ return res

adjust_wh_islr_doc_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
