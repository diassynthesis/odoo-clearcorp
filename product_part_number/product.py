# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import osv,fields
from openerp.tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    
    def create(self, cr, uid, vals, context=None):
        product_template_id = super(product_template, self).create(cr, uid, vals, context=context)

        related_vals = {}       
        if vals.get('part_number'):
            related_vals['part_number'] = vals['part_number']
        if vals.get('manufacturer'):
            related_vals['manufacturer'] = vals['manufacturer']
        if related_vals:
             self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id

    
    _columns = {
        'part_number': fields.related('product_variant_ids', 'part_number', type='char', string='Part Number'),
        'manufacturer':fields.related('product_variant_ids', 'manufacturer', relation='res.partner', type='many2one', string='Manufacturer')
        }

class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        res = {}
        new_args = []
        cont=0

        if not args:
            args = []
        number_params = len(args)

        while cont<number_params:
            param=args[cont]
            if ('part_number' in param) or ('default_code' in param) or ('name' in param):
                search_vals = param[2].split()
                for val in search_vals:
                    new_args = new_args + [[param[0],'ilike', val]]
            cont = cont +1
        if len(new_args) > 0:
            args = new_args
        res = super(product_product, self).search(cr, uid, args, offset, limit, order, context, count)
        return res
        
    _columns = {
        'part_number': fields.char('Part Number', size=90),
        'manufacturer':fields.many2one('res.partner',string="Manufacturer")
    }
    _sql_constraints = [
        ('part_manufacturer_unique','UNIQUE(part_number,manufacturer)','The number part already exist associated to this manufacturer')
        
    ]
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [['default_code','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [['part_number','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [['default_code',operator,name]], limit=limit, context=context))
                if len(ids) < limit:
                    ids.update(self.search(cr, user, args + [['name',operator,name]], limit=(limit-len(ids)), context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

product_product()


