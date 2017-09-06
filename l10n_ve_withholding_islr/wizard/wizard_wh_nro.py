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
import time

class wizard_change_number_wh_islr(osv.osv_memory):
    _name = 'wizard.change.number.wh.islr'
    _description = "Wizard that changes the withholding number"

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        data = super(wizard_change_number_wh_islr, self).default_get(cr, uid, fields, context)
        if context.get('active_model') == 'islr.wh.doc' and context.get('active_id'):
            wh_islr = self.pool.get('islr.wh.doc').browse(cr,uid,context['active_id'],context=context)
            if wh_islr.number:
                nro = wh_islr.number.split('-')
                period = time.strptime(wh_islr.period_id.date_stop,'%Y-%m-%d')
                if len(nro) == 3:
                    new_number = '%04d-%02d-%s' % (period.tm_year, period.tm_mon, nro[2])
                    data.update({'name': new_number})
        return data

    def set_number(self, cr, uid, ids, context):
        data = self.pool.get('wizard.change.number.wh.islr').browse(cr, uid, ids)[0]
        if not data.sure:
            raise osv.except_osv(_("Error!"), _("Please confirm that you want to do this by checking the option"))
        wh_obj = self.pool.get('islr.wh.doc')
        number = data.name
        # validate number format
        len_ok = len(number) == 16
        s_number = number.split('-')
        split_ok = len(s_number) == 3 and \
            sum([x.isdigit() and 1 or 0 for x in s_number]) == 3 and \
            [len(x) for x in s_number] == [4, 2, 8]
        if not(len_ok) or not(split_ok):
            raise osv.except_osv(_("Error!"), _('Invalid number format, please use: AAAA-MM-########'))

        wh_iva = wh_obj.browse(cr, uid, context['active_id'])
        if wh_iva.state != 'done':
            raise osv.except_osv(_("Error!"), _('You can\'t change the number when state <> "Done"'))

        wh_obj.write(cr, uid, context['active_id'], {'number': number}, context=context)
        return {}

    _columns = {
        'name': fields.char('Withholding number', 32, required=True),
        'sure': fields.boolean('Are you sure?'),
    }
wizard_change_number_wh_islr()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
