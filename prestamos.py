# -*- coding: utf-8 -*-
##############################################################################
#
#    Desarrollado por Facultad de Ingeniería Eléctrica
#    Jefe de Laboratorio: M.C. Francisco Rico Andrade
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from osv import osv, fields

class prestamos_marcas_equipos(osv.osv):
	_name="prestamos.marcas.equipos"
	_columns={
	    'name': fields.char("Marca", size=200, required=True),
	    'descripcion': fields.text("Descripción", help="Si la marca requiere una descripción anotala"),
	}
	_sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre de la marca debe de ser unico!'),
    ]
prestamos_marcas_equipos()

class prestamos_tipo_equipos(osv.osv):
    _name="prestamos.tipo.equipos"
    _columns={
        'name': fields.char("Nombre del Equipo", size=200, required=True, help="Agregue el nombre del tipo de equipo. Por ejemplo: Monitor, Teclado, Pinzas, etc"),
        'descripcion': fields.text("Descripción", help="Ponga una descripción al equipo. Ej.- Son monitores CRT de 17 pulgadas."),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre del equipo debe de ser unico!'),
    ]
prestamos_tipo_equipos()

class prestamos_equipo(osv.osv):

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'no_inventario': self.pool.get('ir.sequence').get(cr, uid, 'inventario.in'),
        })
        return super(prestamos_equipo, self).copy(cr, uid, id, default, context=context)

    _name="prestamos.equipo"
    _columns={
        'no_inventario': fields.char("No. Inventario", size=32, required=True, help="Asigne una referencia o número de inventario del equipo."),
        'name': fields.many2one("prestamos.tipo.equipos", "Equipo", required=True),
        'marca': fields.many2one("prestamos.marcas.equipos", "Marca", required=True),
        'modelo': fields.char("Modelo", size=100, help="Si se dispone del modelo del equipo anótelo."),
        'no_serie': fields.char("Serie", size=30, help="Si tiene número de serie anótelo."),
        'snid': fields.char("SNID", size=30),
        'patrimonio': fields.char("No. de Patrimonio", size=30, help="Número de Patrimonio Universitario"),
        'descripcion': fields.text("Descripción"),
        'state': fields.selection((
            ("disponible","Disponible"),
            ("ocupado","Ocupado")
        ), "Estado", readonly=True, help="Mustra si el equipo esta disponible para prestamo o si ya se encuentra ocupado."),
        'prestar': fields.boolean("Para prestar", help="Marque esta casilla si el equipo se puede prestar."),
    }
    _defaults={
        'no_inventario': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'inventario.in'),
        'state': "disponible",
        'prestar': "True",
    }
    _sql_constraints = [
        ('no_inventario_uniq', 'unique(no_inventario)', 'El número de inventario debe de ser unico!'),
    ]
prestamos_equipo()

class prestamos_articulos(osv.osv):
    _name="prestamos.articulos"
    _columns={
        'name': fields.many2one("prestamos.tipo.equipos", "Equipo", required=True, help="Equipo que necesitas."),
        'cantidad': fields.integer("Cantidad", required=True),    
    }
    _defaults={
        'cantidad':1,
    }
prestamos_articulos()
    

class prestamos_solicitud(osv.osv):

    def button_recibir(self, cr, uid, ids, context=None):
        solicitud = self.read(cr, uid, ids, ['state'], context=context)
        for s in solicitud:
            if s['state'] in ['autorizado']:
                self.write(cr, uid, ids, {'state': 'entregado'},context=context)
                fecha = datetime.today()
                self.write(cr, uid, ids, {'fecha_ent': fecha}, context=context)
                self.write(cr, uid, ids, {'usuario_ent': uid}, context=context)
                cr.execute("SELECT id_equipo FROM prestamos_material_prestado WHERE id_solicitud=%s",(s['id'],))
                equipo_ids = map(lambda x: x[0], cr.fetchall())
                object_equipo = self.pool.get('prestamos.equipo')
                object_equipo.write(cr, uid, equipo_ids, {'state': 'disponible'}, context=context)
            else: return False
        return True

    def button_prestar(self, cr, uid, ids, context=None):
        solicitud = self.read(cr, uid, ids, ['state'], context=context)
        for s in solicitud:
            if s['state'] in ['solicitud']:
                self.write(cr, uid, ids, {'state': 'autorizado'},context=context)
                fecha = datetime.today()
                self.write(cr, uid, ids, {'fecha_aut': fecha}, context=context)
                self.write(cr, uid, ids, {'usuario_aut': uid}, context=context)
                material = self.read(cr, uid, ids, ['material'], context=context)
                for m in material:
                    id_lista_material = m['material']
                articulos = self.pool.get('prestamos.articulos')
                lista_material = articulos.read(cr,uid,id_lista_material,context=context)
                for equipo_solicitud in lista_material:
                    cantidad = equipo_solicitud['cantidad']
                    equipo = equipo_solicitud['name'][0]
                    cr.execute("SELECT id FROM prestamos_equipo WHERE name=%s AND state=%s AND prestar limit %s",(equipo, 'disponible', cantidad))
                    equipo_ids = map(lambda x: x[0], cr.fetchall())
                    if(len(equipo_ids)<cantidad):
                        raise osv.except_osv(("¡Material no disponible!"),
                        ('Del equipo "%s" solo hay %s disponibles, tu pediste %s.\nModifica la solicitud, por favor.') % (equipo_solicitud['name'][1], len(equipo_ids), cantidad))
                    material_prestado = self.pool.get('prestamos.material.prestado')
                    for i in equipo_ids:
                        material_prestado.create(cr, uid, vals={'id_solicitud': ids[0], 'id_equipo': i}, context=context)
                    prestamos_equipo = self.pool.get('prestamos.equipo')
                    prestamos_equipo.write(cr, uid, equipo_ids, {'state': 'ocupado'}, context=context)
            else: return False
        return True
        
    def unlink(self, cr, uid, ids, context=None):
        prestamos = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for p in prestamos:
            if p['state'] in ['solicitud']:
                unlink_ids.append(p['id'])
            else: raise osv.except_osv(('¡Acción Invalida!'), ('No es posible eliminar registros que ya han sido autorizados.\nSolo los que esten como solicitud.'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
    _name="prestamos.solicitud"
    _columns={
        'name': fields.char("No. de Solicitud", size=20, required=True),
        'usuario': fields.many2one("res.users", "Solicita", required=True),
        'fecha': fields.datetime("Fecha y Hora", required=True, readonly=True ),
        'state': fields.selection((
                ("autorizado", "AUTORIZADO"),
                ("entregado", "ENTREGADO"),
                ("solicitud", "SOLICITUD")
                ), "Estado", readonly=True),
        'fecha_aut': fields.datetime("Fecha de Autorización", readonly=True, help="Fecha y hora a la que se autorizo entregar el equipo al usuario."),
        'usuario_aut': fields.many2one("res.users", "Autorizo", readonly=True, help="Usuario que autorizo la entrega del material."),
        'fecha_ent': fields.datetime("Fecha de Entrega", readonly=True, help="Fecha y hora a la que se recibio de regreso el equipo prestado."),
        'usuario_ent': fields.many2one("res.users", "Recibio", readonly=True, help="Usuario que recibio de regreso el equipo."),
        'material': fields.many2many("prestamos.articulos", "prestamos_solicitud_articulos", "solicitud_id", "articulos_id", "Lista de Material", required=True, readonly=True, states={'solicitud': [('readonly', False)]}, ondelete="cascade", help="Lista de material que se desea solicitar al laboratorio."),
    }
    
    _defaults={
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'prestamos.op'),
        'usuario': lambda obj, cr, uid, context: uid,
        'fecha': fields.datetime.now,
        'state': 'solicitud',
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El número de solicitud debe de ser unico!'),
    ]
    _order = 'name desc'
prestamos_solicitud()

class prestamos_material_prestado(osv.osv):
    
    _name="prestamos.material.prestado"
    _columns={
        'id_solicitud': fields.many2one("prestamos.solicitud", "Número de Solicitud", readonly=True),
        'id_equipo': fields.many2one("prestamos.equipo", "Material", readonly=True),
    }
    
    _rec_name="id_solicitud"
    
prestamos_material_prestado()
