#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################

from report import report_sxw
from osv import osv

class rep_comprobante_islr(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rep_comprobante_islr, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_address': self._get_address,
            'get_period': self._get_period,
        })

    def _get_address(self, address):
        """This address must be a res.partner.address instance"""
        return self.pool.get('res.partner').\
            get_partner_address(self.cr, self.uid, address)

    def _get_period(self, period):
        date = period.date_stop.split('-')
        return '%s/%s' % (date[1], date[0])

report_sxw.report_sxw(
    'report.islr.wh.doc',
    'islr.wh.doc',
    'addons/l10n_ve_withholding_islr/report/wh_islr_report.rml',
    parser=rep_comprobante_islr,
    header=False
)

