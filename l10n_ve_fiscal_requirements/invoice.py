#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################

from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):


    def _unique_invoice_per_partner(self, cr, uid, ids, context=None):
        if context is None: context={}
        inv_brw = self.browse(cr, uid, ids, context=context)
        ids_ivo = []
        for inv in inv_brw:
            ids_ivo.append(inv.id)
            if inv.type in ('out_invoice','out_refund'):
                return True
            inv_ids = inv.nro_ctrl is not '' and inv.nro_ctrl is not False and inv.reference is not False and self.search(cr,uid,
                        ['|',('nro_ctrl','=',inv.nro_ctrl and inv.nro_ctrl.strip() ),('reference','=',inv.reference and inv.reference.strip()),
                        ('type','=',inv.type),
                        ('partner_id','=',inv.partner_id.id)],
                        context=context) or []
            if [True for i in inv_ids if i not in ids_ivo ] and inv_ids:
                return False
        return True

    def _unique_supplier_invoice_number(self, cr, uid, ids, context=None):
        if context is None: context={}
        inv_brw = self.browse(cr, uid, ids, context=context)
        for inv in inv_brw:
            if inv.type in ('out_invoice', 'out_refund'):
                return True
            inv_ids = self.search(
                cr, uid, [
                ('supplier_invoice_number', '=', inv.supplier_invoice_number),
                ('type', '=', inv.type),
                ('partner_id', '=', inv.partner_id.id),
                ('id', '!=', inv.id)
                ], context=context)
            return not inv_ids
        return True


    _inherit = 'account.invoice'
    _columns = {
        'nro_ctrl': fields.char('Control Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Code used for intern invoice control"),
        'sin_cred': fields.boolean('Tax-exempt?', readonly=False, help="Set it true if the invoices V.A.T. exempt"),
        'parent_id':fields.many2one('account.invoice', 'Parent Invoice', readonly=True, states={'draft':[('readonly',False)]}, help='When this field has information, this invoice is a credit note or debit note. This field is used to reference to the invoice that originated this credit note or debit note.'),
        'child_ids':fields.one2many('account.invoice', 'parent_id', 'Debit and Credit Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'supplier_invoice_number': fields.char('Supplier Invoice Number', size=64, help="The reference of this invoice as provided by the supplier.", readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date("Document's Date", help="Emmission date, generally is the date printed on invoice, this date is used to show in the Purchase Fiscal book", select=True),
        'invoice_printer' : fields.char('Fiscal printer invoice number', size=64, required=False,help="Fiscal printer invoice number, is the number of the invoice on the fiscal printer"),
        #TODO": maybe it must be a many2one to declared FiscalPrinter when FiscalV is ready
        'fiscal_printer' : fields.char('Fiscal printer number', size=64, required=False,help="Fiscal printer number, generally is the id number of the printer."),
        'loc_req':fields.boolean('Required by Localization', help='This fields is for technical use'),
        'z_report': fields.char(string='Report Z', size=64, help=""),

    }


    _constraints = [
        (_unique_invoice_per_partner, _('The Document you have been entering for this Partner has already been recorded'),['Numero de Control (nro_ctrl)','Referencia (reference)']),
        (_unique_supplier_invoice_number, _('The Number you have been entering for this Partner has already been recorded'),['Numero (supplier_invoice_number)','Empresa (partner_id)']),
         ]

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=100):
        #~ Based on account.account.name_search...
        res = super(account_invoice, self).name_search(
            cr, user, name, args, operator, context, limit)
        if not res and name:
            ids = self.search(
                cr, user, [('supplier_invoice_number', operator, name)] + args,
                limit=limit, context=context)
            if ids:
                res = self.name_get(cr, user, ids, context=context)
        return res

    def _refund_cleanup_lines(self, cr, uid, lines):
        """
        Metodo created to clean invoice lines
        """
        for line in lines:
            del line['id']
            del line['invoice_id']
            #TODO Verify one more elegant way to do this
            for field in ('company_id', 'partner_id', 'account_id', 'product_id',
                          'uos_id', 'account_analytic_id', 'tax_code_id', 'base_code_id',
                          "concept_id","tax_id"):
                line[field] = line.get(field, False) and line[field][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6,0, line.get('invoice_line_tax_id', [])) ]
        return map(lambda x: (0,0,x), lines)

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'child_ids':[],
            'nro_ctrl': False,
            'reference': False,
            'supplier_invoice_number': False,
            })
        res = super(account_invoice, self).copy(cr, uid, id, default, context)
        return res


    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('type') in ('out_invoice','out_refund') and vals.get('date_invoice') and not vals.get('date_document'):
            vals.update({'date_document':vals['date_invoice']})
        return super(account_invoice, self).write(cr, uid, ids, vals, context)

account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
