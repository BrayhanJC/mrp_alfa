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

	_inherit = 'stock.move'

	warehouse_quantity = fields.Char(compute='_get_warehouse_quantity', string='Cantidad en Almacenes')

	def _get_warehouse_quantity(self):
		_logger.info('estamos entrando')
		for record in self:
			warehouse_quantity_text = ''
			product_id = record.product_id.id
			if product_id:
				quant_ids = self.env['stock.quant'].sudo().search([('product_id', '=', product_id),('location_id.usage','=','internal')])
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

