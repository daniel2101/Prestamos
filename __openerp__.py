# -*- coding: utf-8 -*-
##############################################################################
#
#    Desarrollado por Facultad de Ingeniería Eléctrica
#    Jefe de Proyecto: M.C. Francisco Rico Andrade
#    Desarrollador: Ing. Salvador Daniel Pelayo Gómez.
#
##############################################################################
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


{
    "name" : "Prestamos",
    "version" : "0.6",
    "depends": ["base"],
    "author" : "Salvador Daniel Pelayo Gómez",
    "website": "http://lr.fie.umich.mx",
    "category" : "Generic Modules/Others",
    "description" : """
Modulo para llevar el control de prestamos en el Laboratorio de Redes y Comunicaciones.
""",
    "init_xml" : [],
    "update_xml" : ["prestamos_menu.xml",
                    "prestamos_secuencias.xml",
                    "security/event_security.xml",
                    "security/ir.model.access.csv",
                    "prestamos_view.xml",
                    "prestamos_report.xml",
                    ],
    "demo_xml" : [],
    "installable" : True,
    'auto_install': False,
    'application': True,
}
