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

import time
from osv import osv
from report import report_sxw

class prestamos_inv_res(report_sxw.rml_parse):

    def datos(self, cr, uid, name):
        cr.execute("SELECT prestamos_tipo_equipos.name AS nombre, prestamos_equipo.modelo AS modelo, prestamos_marcas_equipos.name AS mar, COUNT(*) AS total FROM prestamos_equipo, prestamos_tipo_equipos, prestamos_marcas_equipos WHERE prestamos_equipo.name = prestamos_tipo_equipos.id AND prestamos_equipo.marca = prestamos_marcas_equipos.id GROUP BY nombre, modelo, mar;")
        equipos = map(lambda x: x, cr.fetchall())
        #raise osv.except_osv("Algo", equipos)
        return equipos 
        
    def __init__(self, cr, uid, name, context=None):
        super(prestamos_inv_res, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'datos': self.datos(cr, uid, name),
            'time': time,
        })

report_sxw.report_sxw('report.prestamos.equipo', 'prestamos.equipo', 'addons/Prestamos/report/inventario_resumido.rml', parser=prestamos_inv_res, header="external")
report_sxw.report_sxw('report.prestamos.equipo.completo', 'prestamos.equipo', 'addons/Prestamos/report/inventario_equipo.rml', parser=prestamos_inv_res, header="external")
