#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Javier Duran              <javier@nvauxoo.com>
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

import time
import pooler
from report import report_sxw
from tools.translate import _

class list_wh_iva(report_sxw.rml_parse):
    
    total_amount_exempt=0
    total_amount_untaxed=0
    
    def __init__(self, cr, uid, name, context):
        super(list_wh_iva, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_type_doc': self._get_type_document,
            'get_doc_number':self._get_document_number,
            'get_doc_affected':self._get_document_affected,
            'get_ctrl_number':self._get_control_number,
            'get_alicuota':self._get_alicuota,
            'get_amount_exempt':self._get_amount_exempt,
            'get_total_amount_exempt':self._get_total_amount_exempt,
            'get_amount_untaxed':self._get_amount_untaxed,
            'get_total_amount_untaxed':self._get_total_amount_untaxed,
            'get_total_amount_doc':self._get_total_amount_doc,
        })
        
    def _get_total_amount_doc(self,doc_id):
        total=0
        for line in self.pool.get('txt.iva').browse(self.cr,self.uid, doc_id).txt_ids:
            total+=line.invoice_id.amount_total
        return total
        
    def _get_alicuota(self,txt_line):
        return self.pool.get('txt.iva').get_alicuota(self.cr,self.uid,txt_line)
        
    def _get_amount_exempt(self,txt_line):
        amount_exempt,amount_untaxed = self.pool.get('txt.iva').get_amount_exempt_document(self.cr,self.uid,txt_line)
        self.total_amount_exempt+=amount_exempt
        return amount_exempt

    def _get_total_amount_exempt(self):
        return self.total_amount_exempt

    def _get_amount_untaxed(self,txt_line):
        amount_exempt,amount_untaxed = self.pool.get('txt.iva').get_amount_exempt_document(self.cr,self.uid,txt_line)
        self.total_amount_untaxed+=amount_untaxed
        return amount_untaxed
        
    def _get_total_amount_untaxed(self):
        return self.total_amount_untaxed
                
    def _get_control_number(self,txt_line):
        return self.pool.get('txt.iva').get_number(self.cr,self.uid,txt_line.invoice_id.nro_ctrl,'inv_ctrl',20)    

    def _get_type_document(self,line):
        return self.pool.get('txt.iva').get_type_document(self.cr,self.uid,line)

    def _get_document_number(self,txt_id,txt_line):
        return self.pool.get('txt.iva').get_document_number(self.cr,self.uid,txt_id,txt_line,'inv_number')

    def _get_document_affected(self,line):
        return self.pool.get('txt.iva').get_document_affected(self.cr,self.uid,line)

report_sxw.report_sxw(
    'report.list_report_wh_vat2',
    'txt.iva',
    'addons/l10n_ve_withholding_iva/report/list_wh_iva_report.rml',
    parser=list_wh_iva, 
    header=False
)
