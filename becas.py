# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
#/#############################################################################
from osv import osv, fields
import pooler
import time
import netsvc
import logging
logging.basicConfig(level=logging.INFO)

class process_becas(osv.osv):
    _name = 'process.becas'
    _inherit = ['mail.thread']
    _rec_name = 'nobeca'

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state': 'd',
            'nobeca': self.pool.get('ir.sequence').get(cr, uid, 'becas'),
        })
        return super(process_becas, self).copy(cr, uid, id, default, context=context)

    _columns = {

            'state': fields.selection([('d','Borrador'),('p','Pendiente de Autorizar'),('a','Autorizado'),('c','Cancelado')],readonly=True,select=True, string='State'),
            'date': fields.date(string='Fecha', state={'a': [('readonly', True)]}),
            'student_id': fields.many2one('op.student', string='Student', state={'a': [('readonly', True)]}),
            'obs': fields.text(string='Observaciones', state={'a': [('readonly', True)]}),
            'autorizo': fields.char(string='Autorizo', state={'a': [('readonly', True)]}),
            'nobeca': fields.char('# de Beca', readonly=True),

    }

    _defaults = {
                 'nobeca': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'becas'),
                 'state':'d',
                 'date': time.strftime('%Y-%m-%d'),
    }

    _order = "nobeca desc"



    def in_progress(self, cr, uid, ids, context=None):
        logging.info('IN PROGRESS' )
        self.write(cr,uid,ids,{'state':'p'})
        return True

    def confirm_cancel(self, cr, uid, ids, context=None):
        logging.info('CANCELADA' )
        self.write(cr,uid,ids,{'state':'c'})
        return True

    def authorized(self, cr, uid, ids, context=None):
        logging.info('AUTORIZADA' )
        self.write(cr,uid,ids,{'state':'a'})
        #aqui voy a asignar la beca al niño
        return True

    '''def confirm_selection(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        student_pool = self.pool.get('op.student')
        for field in self.browse(cr, uid, ids, context=context):
            if field.standard_id is False or field.standard_id is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar el Grado o Seccion'))
            elif field.category_id is False or field.category_id is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar la Categoria'))
            elif field.batch_id is False or field.batch_id is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar el Ciclo Escolar'))
            elif field.course_id is False or field.course_id is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar la Seccion'))
            elif field.gender is False or field.gender is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar el Genero del Alumno'))
            elif field.birth_date is False or field.birth_date is None:
                raise osv.except_osv(('Error'), ('Es necesario indicar la Fecha de Nacimiento del Alumno'))

            if field.gr_no == True:
                gr = field.gr_no_old
            else:
                gr = field.gr_no_new
            vals = {
                    'title': field.title and field.title.id or False,
                    'name': field.name,
                    'middle_name': field.middle_name,
                    'last_name': field.last_name,
                    'birth_date':field.birth_date,
                    'gender': field.gender,
                    'category': field.category_id and field.category_id.id or False,
                    'course_id': field.course_id and field.course_id.id or False,
                    'batch_id': field.batch_id and field.batch_id.id or False,
                    'standard_id': field.standard_id and field.standard_id.id or False,
                    'religion': field.religion_id and field.religion_id.id or False,
                    'photo': field.photo or False,

                    'gr': gr,
                    'id_number': field.matricula or False,
                    'address':[(0,0,{
                                     'type': 'contact',
                                     'street': field.street or False,
                                     'street2': field.street2 or False,
                                     'phone': field.phone or False,
                                     'mobile': field.mobile or False,
                                     'zip': field.zip or False,
                                     'city_id': field.city.id or False,
                                     'country_id': field.country_id and field.country_id.id or False,
                                     'state_id': field.state_id and field.state_id.id or False,
                                     })],
                    #SALUD
                    'med_name': field.doctor or False,
                    'med_tel': field.doctor_phone or False,
                    'med_email': field.doctor_address or False,
                    'forecast': field.emergency_name or False,
                    'blood_type': field.blood_type or False,
                    'age': field.years_student or False,
                    #OTROS DATOS
                    'vive_con': field.lives_with or False,
                    'vive_con_cuantos': field.cuantos_viven or False,
                    'nationality': field.nacionalidad.id or False,
                    'gr_no': field.curp or False,

                    'sube_en':field.where_board,
                    'baja_en': field.where_down,
                    'num_viajes':field.how_many_trips,
                    'ruta_am': field.way_am,
                    'ruta_pm': field.way_pm,
                    'sale_solo': field.out_alone,
                    'entregan_en': field.delivered,
                    'recogen_en':field.collect,
                }

        new_student = student_pool.create(cr, uid, vals, context=context)
        self.write(cr,uid,ids,{'state':'s', 'student_id': new_student, 'nbr': 1})

        admission_pool = self.pool.get('op.admission')
        admission_obj=admission_pool.browse(cr, uid, ids[0], context=context)
        for invoice in self.browse(cr, uid, ids, context=context):   #SI EL INVOICE NO ES EL PAPA CREAMOS UN RES PARTNER
            if(invoice.invoice_name is not False and invoice.invoice_rfc is not False):
                if(len(invoice.invoice_name)!= 0):
                    partner_invoice_pool = self.pool.get('res.partner')
                    partner_invoice_obj=partner_invoice_pool.browse(cr, uid, ids[0], context=context)
                    vals_invoice = {
                        'name':invoice.invoice_name,
                        'type':'invoice',
                        'street':invoice.street_invoice,
                        'l10n_mx_street3':invoice.numero_invoice,
                        'l10n_mx_street4':invoice.numero_int_invoice,
                        'street2':invoice.street2_invoice,
                        'city_id':invoice.city_invoice.id,
                        'city':invoice.city_invoice.name,
                        'state_id':invoice.state_id_invoice.id,
                        'zip':invoice.zip_invoice,
                        'vat':'MX'+invoice.invoice_rfc,
                        'regimen_fiscal_id':invoice.invoice_taxation.id,
                    }

                    new_partner = partner_invoice_pool.create(cr, uid, vals_invoice, context=context)

        #Aqui creamos el res_partner del papa parent_admission
        #Hago el for para sacar a todos los papas
        if admission_obj.parent_admission is False or admission_obj.parent_admission is None:
            raise osv.except_osv(('Error'), ('El Alumno no tiene padres relacionados'))

        for parent in admission_obj.parent_admission:

            #si el campo exist_father no tiene nada creamos el rest parner.
            partner_pool = self.pool.get('res.partner')
            partner_obj=partner_pool.browse(cr, uid, ids[0], context=context)
            subjected=False
            invoice=False
            parent_student=0

            if parent.apoderado_admin is False :
                subjected=False
            else:
                subjected=True


            #revisamos si el papa es nuevo o ya existe
            if parent.check_exist_father == False:
                type_parent="contact"
                #si el papa es apoderado administrativo el tipo de direccion es invoice
                if parent.apoderado_admin == True:
                   type_parent="invoice"

                parentesco='';
                if parent.parent_type == 'Madre':
                    parentesco='Madre'
                elif parent.parent_type == 'Padre' :
                    parentesco='Padre'
                else:
                    raise osv.except_osv(('Error'), ('Es necesario seleccionar el parentesco del Padre o Madre'))
                vat_parent=''
                if parent.rfc is  False or parent.rfc is  None:
                        vat_parent= 'MXXAXX010101000'
                else:
                        vat_parent='MX'+ parent.rfc

                valores = {
                           #direccion
                            'street': parent.street or False,
                            'street2': parent.street2 or False,
                            'l10n_mx_city2': parent.street or False,
                            'l10n_mx_street3':  parent.numero or False,
                            'l10n_mx_street4':parent.interior or False,
                            'city': parent.city.name or False,#text
                            'city_id': parent.city.id or False,
                            'zip': parent.zip or False,
                            'state_id': parent.state_id.id or False,
                            'country_id': parent.country_id.id or False,

                            #datos personales
                            'name': parent.name or False,
                            'display_name': parent.name or False,
                            'email': parent.email or False,
                            'phone': parent.phone or False,
                            'mobile': parent.mobile or False,

                            #datos de facturacion
                            'vat_subjected': subjected ,
                            'vat': vat_parent,
                            #'regimen_fiscal_id': parent.regimen_fiscal_id or False,
                            'type': type_parent,

                            #otros
                            'comment': parentesco,
                            'customer': True,
                            'is_company': True,
                            'apoderado_admon': parent.apoderado_admin or False,
                            'apoderado_aca': parent.apoderado_acad or False,

                            'ean13': new_student or False,

                        }
                new_partner = partner_pool.create(cr, uid, valores, context=context)
                parent_student=new_partner
                logging.info('creado')
                #LA RELACION PARA SER PADRE SE GENERA EN EL TRIGGER GENERATE_USER_PARENTS

                #CREAR NUEVOS CAMPOS PARA PARENT
                cr.execute("select id from op_parent where name='%s'",(parent_student,))
                logging.info("select id from op_parent where name='%s'",(parent_student,))
                response=cr.fetchone()
                id_opparent_table = response[0]
                if response is None:
                     logging.info('no hay id del parent!!!!')
                else:
                    #HACEMOS ACTUALIZACION A OP PARENT
                     brand_car = parent.brand_car or False
                     schedule = parent.schedule  or False
                     grade = parent.grade  or False
                     house = parent.house  or False
                     company = parent.company  or False
                     job = parent.job  or False
                     rent = parent.rent  or False
                     student = parent.student  or False
                     ocupation = parent.ocupation  or False
                     monthly_income = parent.monthly_income  or 0.00
                     car = parent.car  or False
                     marital_status = parent.marital_status  or False
                     generation = parent.generation  or False
                     model_car = parent.model_car  or False
                     department = parent.department  or False
                     cr.execute("UPDATE op_parent set brand_car = %s,schedule = %s,grade = %s,house = %s,company = %s,job = %s,rent = %s,student = %s,ocupation = %s,monthly_income = %s,car = %s,marital_status = %s,generation = %s,model_car = %s,department = %s WHERE id = '%s'",(brand_car,schedule,grade,house,company,job,rent,student,ocupation,monthly_income,car,marital_status,generation,model_car,department,id_opparent_table, ))

            else:
                #BUSCAR EL ID DEL PARENT
                cr.execute("select  op.id from  res_partner par join res_users us on par.id=us.partner_id join op_parent op on us.id=op.user_id where par.id=%s",(parent.exist_father.id,))
                logging.info('select  op.id from  res_partner par join res_users us on par.id=us.partner_id join op_parent op on us.id=op.user_id where par.id=%s',parent.exist_father.id)
                response=cr.fetchone()
                logging.info('R1: ')
                logging.info(response)

                if response is None:
                    mensaje='El Padre no existe! Asegurate de haber seleccionado bien el campo padre existente'
                    raise osv.except_osv(('Error'), (mensaje ))
                else:
                    op_parent_id = response[0]
                    cr.execute("INSERT INTO op_parent_student_rel (op_parent_id,op_student_id) VALUES (%s,%s)",(new_student,op_parent_id))



        return True'''''





    ''''def open_student(self, cr, uid, ids,context={}):

        this_obj = self.browse(cr, uid, ids[0], context)
        student = self.pool.get('op.student').browse(cr, uid, this_obj.student_id.id, context)
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'openeducat_erp', 'view_op_student_form')
        tree_view = models_data.get_object_reference(cr, uid, 'openeducat_erp', 'view_op_student_tree')
        value = {
                'domain': str([('id', '=', student.id)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'op.student',
                'view_id': False,
                'views': [(form_view and form_view[1] or False, 'form'),
                          (tree_view and tree_view[1] or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': student.id,
                'target': 'current',
                'nodestroy': True
            }
        self.write(cr,uid,ids,{'state':'done'})
        return value'''

process_becas()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
#xpandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
