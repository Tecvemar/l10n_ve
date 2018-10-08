#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
################ Credits ######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#                    Katherine Zsoral <katherine.zaoral@vauxoo.com>
#    Planified by: Nhomar Hernandez
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                 help="Fiscal Book where this line is" \
                                 " related to"),
        'issue_fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                       help="Fiscal Book where this invoice" \
                                       " needs to be add"),
        # TODO: THIS FIELD TO BE CHANGED TO A STORABLE FUNCTIONAL FIELD
        # CHANGE EVEN FROM boolean to selection
        'fb_submitted': fields.boolean('Fiscal Book Submitted?',
                                       help="Indicates if this invoice is in" \
                                       " a Fiscal Book which has being" \
                                       " already submitted to the statutory" \
                                       " institute"),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first in the invoice have a fiscal book associated and if
        the sate of the book is in cancel. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if not inv_brw.fb_id or (inv_brw.fb_id and inv_brw.fb_id.state == 'cancel'):
                super(account_invoice, self).action_cancel(cr, uid, ids)
            else:
                raise osv.except_osv(_("Error!"),
                _("You can't cancel an invoice that is loaded in a processed"
                  "Fiscal Book. You need to go to Fiscal Book and set the book"
                  " to Draft. Then you could be able to cancel the invoice."))
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'fb_id': 0,
            'issue_fb_id': 0,
            'fb_submitted': False,
            })
        return super(account_invoice, self).\
            copy(cr, uid, id, default, context=context)

account_invoice()
