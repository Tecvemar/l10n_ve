#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              María Gabriela Quilarque  <gabriela@vauxoo.com>
#              Nhomar Hernandez          <nhomar@vauxoo.com>
#    Planified by: Humberto Arocha
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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'jour_id': fields.many2one('account.journal', 'Journal',required=False,help="Default journal for damaged invoices"),
        'acc_id': fields.many2one('account.account', 'Account',required=False,help="Default account used for invoices and lines from damaged invoices"),
        'printer_fiscal' : fields.boolean('Manages fiscal printer', help='Indicates that the company can operate a fiscal printer'),
        }
res_company()

