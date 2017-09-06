#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Javier Duran              <javier@vauxoo.com>
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

{
    "name" : "Automatically Calculation Withholding Income",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "General",
    "website": "http://wiki.openerp.org.ve/",
    "description": ''' - Generate the voucher of withholding income to validate the invoice.
 - Generate the report of voucher of withholding income.
 - Generate the file .xml required by the Venezuelan laws, for agent of withholding income specials.
 - Generate view for load the concepts of wittholding whith their rates.
 - Generate view for visualize the withholding income for suppilers and customers.
 - Load data of the 86 concepts of wittholdings whith their rates.

If you want be able to propose withholding concepts from sales and purchases you must install extra module @section{l10n_ve_sale_purchase}.

''',
    "depends" : ["account", "l10n_ve_withholding", "product"],
    "init_xml" : [],
    "demo_xml":[
            "demo/l10n_ve_islr_withholding_demo.xml",
               ],
    "update_xml" : [
            "view/installer.xml",
            "islr_wh_report.xml",
            "security/wh_islr_security.xml",
            "security/ir.model.access.csv",
            "data/l10n_ve_islr_withholding_data.xml",
            "retencion_islr_sequence.xml",
            "wizard/wizard_wh_nro_view.xml",
            "wizard/adjust_wh_islr_doc.xml",
            "wizard/employee_income_wh.xml",
            "view/wh_islr_view.xml",
            "view/invoice_view.xml",
            "view/partner_view.xml",
            "view/islr_wh_doc_view.xml",
            "view/islr_wh_concept_view.xml",
            "view/product_view.xml",
            "view/islr_xml_wh.xml",
            "workflow/islr_wh_workflow.xml",
            "workflow/wh_action_server.xml",
            "report/l10n_ve_tcv_arcv.xml",
    ],
    "active": False,
    "installable": True
}
