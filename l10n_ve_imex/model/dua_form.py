# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan Márquez
#    Creation Date: 2014-10-10
#    Version: 0.0.0.1
#
#    Description:
#
#
##############################################################################

from datetime import datetime
from osv import fields, osv
from tools.translate import _
import pooler
import decimal_precision as dp
import time
import netsvc

##------------------------------------------------------------------ dua_form


class dua_form(osv.osv):

    _name = 'dua.form'

    _description = ''

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    def name_get(self, cr, uid, ids, context):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        for item in self.browse(cr, uid, ids, context={}):
            res.append((item.id, '%s (%s)' % (item.name, item.date)))
        return res

    ##--------------------------------------------------------- function fields

    _columns = {
        'name': fields.char(
            'Number', size=64, required=True, readonly=False,
            help="DUA Number"),
        'date': fields.date(
            'Date', required=True, readonly=False, select=True),
        'agent_partner_id': fields.many2one(
            'res.partner', 'Customs Agent\'s', required=False,
            ondelete='restrict', help="Customs Agent's"),
        'ref': fields.char(
            'Reference', size=64, required=True, readonly=False,
            help="Customs Agent's expedient number"),
        'customs_form_ids': fields.one2many(
            'customs.form', 'dua_form_id', 'SENIAT - Forms'),
        'invoice_ids': fields.one2many(
            'account.invoice', 'dua_form_id', 'Invoices'),
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

dua_form()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
