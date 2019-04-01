# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) Brayhan Jaramillo.
#               brayhanjaramillo@hotmail.com


{
    'name': 'Mrp Generate PO',
    'version': '10,0',
    'category': 'Create PO',
    'description': '',
    'author': 'Brayhan Andres Jaramillo Castaño',
    'depends': [ 'mrp', 'base'
    ],

    'data': [
        'views/mrp_production_inherit_view.xml',

    ],
    'installable': True,
}
