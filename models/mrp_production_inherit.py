# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) Brayhan Jaramillo.
#               brayhanjaramillo@hotmail.com


from odoo import api, fields, models, _
import time
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, AccessError, ValidationError


class MrpProductionInherit(models.Model):

	_inherit = 'mrp.production'

	check_po= fields.Boolean(string="Generar Orden de Compra", default=False)
	
	partner_id = fields.Many2one('res.partner', string='Proveedor', change_default=True, track_visibility='always')
	
	warehouse_quantity = fields.Char(compute='_get_warehouse_quantity', string='Quantity per warehouse')


	def _get_warehouse_quantity(self):
		for record in self:
			warehouse_quantity_text = ''
			product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
			if product_id:
				quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id[0].id),('location_id.usage','=','internal')])
				t_warehouses = {}
				for quant in quant_ids:
					if quant.location_id:
						if quant.location_id not in t_warehouses:
							t_warehouses.update({quant.location_id:0})
						t_warehouses[quant.location_id] += quant.qty

				tt_warehouses = {}
				for location in t_warehouses:
					warehouse = False
					location1 = location
					while (not warehouse and location1):
						warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
						if len(warehouse_id) > 0:
							warehouse = True
						else:
							warehouse = False
						location1 = location1.location_id
					if warehouse_id:
						if warehouse_id.name not in tt_warehouses:
							tt_warehouses.update({warehouse_id.name:0})
						tt_warehouses[warehouse_id.name] += t_warehouses[location]

				for item in tt_warehouses:
					if tt_warehouses[item] != 0:
						warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + str(tt_warehouses[item])
				record.warehouse_quantity = warehouse_quantity_text


	def generate_purchase_order(self):

		data_product=[]
		date_current= fields.Datetime.now()

		currency_id= self.env['res.currency'].search([('name', '=', 'COP')])
		if self.move_raw_ids:
			if self.partner_id:
				for x in self.move_raw_ids:
					if x.quantity_available < x.product_uom_qty:

						name = x.product_id.name
						if x.product_id.code:
							name = '[%s] %s' % (name, x.product_id.code)
						if x.product_id.description_purchase:
							name += '\n' + x.product_id.description_purchase

						data={'product_id': x.product_id.id, 'product_uom':x.product_id.uom_id.id, 'price_unit': x.product_id.list_price, 'product_qty':0, 'name': name, 'date_planned': date_current}
						data_product.append( (0,_ ,data) )

				vals={	'partner_id': self.partner_id.id,
						'currency_id': currency_id.id,
						'date_planned': date_current,
						'order_line': data_product
					}

				_logger.info(vals)

				self.env['purchase.order'].create(vals)
			else:

				raise UserError(_("Debe seleccionar un proveedor para poder generar una Orden de Compra"))

