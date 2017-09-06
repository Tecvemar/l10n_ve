# -*- coding: utf-8 -*-
##############################################################################
#
#
#    Programmed by: Alexander Olivares <olivaresa@gmail.com>
#
#    This the script to connect with Seniat website
#    for consult the rif asociated with a partner was taken from:
#
#    http://siv.cenditel.gob.ve/svn/sigesic/ramas/sigesic-1.1.x/sigesic/apps/comun/seniat.py
#
#    This script was modify by:
#                   Javier Duran <javier@vauxoo.com>
#                   Miguel Delgado <miguel@openerp.com.ve>
#                   Israel Fermín Montilla <israel@openerp.com.ve>
#                   Juan Márquez <jmarquez@tecvemar.com.ve>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import re
import decimal_precision as dp


class res_partner_address(osv.osv):
    _inherit='res.partner.address'

    '''
    Invoice Address uniqueness check
    '''
    def _check_addr_invoice(self,cr,uid,ids,context={}):
        obj_addr = self.browse(cr,uid,ids[0])
        if obj_addr.partner_id.vat and obj_addr.partner_id.vat[:2].upper() == 'VE':
            if obj_addr.type == 'invoice':
                cr.execute('select id,type from res_partner_address where partner_id=%s and type=%s', (obj_addr.partner_id.id, obj_addr.type))
                res=dict(cr.fetchall())
                if (len(res) == 1):
                    res.pop(ids[0],False)
                if res:
                    return False
        return True


    _constraints = [
        (_check_addr_invoice, _('Error ! The partner already has an invoice address.'), [])
    ]

res_partner_address()


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'seniat_updated': fields.boolean('Seniat Updated', help="This field indicates if partner was updated using SENIAT button"),
        'wh_iva_rate': fields.float(
            string='Rate',
            digits_compute=dp.get_precision('Withhold'),
            help="Vat Withholding rate"),
        'wh_iva_agent': fields.boolean('Wh. Agent',
            help="Indicate if the partner is a withholding vat agent"),
    }

    _default = {
        'seniat_updated': False,
    }

    def vat_cleaner_ve(self,vat):
        return vat.replace('-','').replace(' ','').replace('/','').upper().strip()

    def name_search(self,cr,uid,name='',args=[],operator='ilike',context=None,limit=80):
        if context is None:
            context={}
        ids= []
        if len(name) >= 2:
            ids = self.search(cr, uid, [('vat',operator,name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr,uid,[('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr,uid,ids,context=context)

    '''
    Required Invoice Address
    '''
    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE':
            if hasattr(partner_obj, 'address'):
                res = [addr for addr in partner_obj.address if addr.type == 'invoice']
                if res:
                    return True
                else:
                    return False
            else:
                return True
        return True

    def _check_vat_uniqueness(self, cr, uid, ids, context={}):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        partner_obj = self.pool.get('res.partner')
        partner_brw = partner_obj.browse(cr,uid,ids,context=context)[0]
        current_vat = partner_brw.vat if partner_brw.vat else ''
        if not current_vat or not 'VE' in [a.country_id.code for a in partner_brw.address]:
            return True # Accept empty and foreign VAT's
        current_vat = self.vat_cleaner_ve(current_vat)
        duplicates = partner_obj.search(cr, uid, [('vat', '=', current_vat),('id','!=',partner_brw.id)])
        return not duplicates

    _constraints = [
        (_check_partner_invoice_addr, _('Error ! The partner does not have an invoice address.'), []),
        (_check_vat_uniqueness, _("Error ! Partner's VAT must be a unique value or empty"), []),
    ]

    def vat_change_fiscal_requirements(self, cr, uid, ids, value, context=None):
        if context is None:
            context={}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not value:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=context)
        res = self.search(cr, uid, [('vat', 'ilike', value), ('id', 'not in', ids)])
        if res:
            rp = self.browse(cr, uid, res[0],context=context)
            return {'warning':  {
                                'title':_('Vat Error !'),
                                'message': _('The VAT [%s] looks like [%s] ' +
                                             'which is already being used ' +
                                             'by: %s') %
                                             (value, rp.vat.upper(),
                                              rp.name.upper())
                                }
                   }
        else:
            res = super(res_partner,self).vat_change(cr, uid, ids, value, context=context)
            res['value'].update({'vat':self.vat_cleaner_ve(value)})
            return res

    def check_vat_ve(self, vat, context = None):
        '''
        Check Venezuelan VAT number, locally caled RIF.
        RIF: JXXXXXXXXX RIF CEDULA VENEZOLANO: VXXXXXXXXX CEDULA EXTRANJERO: EXXXXXXXXX
        '''

        def compute_vat_ve(vat2):
            '''
            Toma un nro de cedula o rif y calcula el digito validador
            data: string con numero de CI o RIF sin espacios ni guiones ej.
                V12345678
                E12345678
                J123456789
            devuelve el rif con el digito calculado
            no se validan los datos de entrada
            para validar: if data == calcular_rif(data):
            '''
            _OPER_RIF = [4, 3, 2, 7, 6, 5, 4, 3, 2]
            items = [' VEJPG'.find(vat2[0])]
            items.extend(map(lambda x: int(x), vat2[1:]))
            val = sum(i * o for (i, o) in zip(items, _OPER_RIF))
            digit = 11 - (val % 11)
            digit = digit if digit < 10 else 0
            return '%s%s' % (vat2[:9], digit)

        res = False
        if context is None:
            context={}
        if re.search(r'^[VEJPG][0-9]{9}$', vat):
            context.update({'ci_pas':False})
            res = True
        if re.search(r'^([0-9]{1,8}|[D][0-9]{9})$', vat):
            context.update({'ci_pas':True})
            res = True
        if vat and res and len(vat) == 10:
            res = vat == compute_vat_ve(vat)
        return res

    def update_rif(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        su_obj = self.pool.get('seniat.url')
        return su_obj.update_rif(cr, uid, ids, context=context)


    def create(self, cr, uid, vals, context=None):
        if vals.get('vat'):
            vals.update({'vat': self.vat_cleaner_ve(vals.get('vat',''))})
        res = super(res_partner, self).create(cr, uid, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('vat'):
            vals.update({'vat':self.vat_cleaner_ve(vals.get('vat',''))})
        res = super(res_partner, self).write(cr, uid, ids, vals, context)
        return res

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
