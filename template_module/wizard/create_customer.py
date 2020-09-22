# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

# import logging
# _logger = logging.getLogger(__name__)

class CreateCustomer(models.TransientModel):
	_name = 'create.customer'
	_description = 'Create a new visitor on customers'
	
	nombre = fields.Char("Name")
	fname = fields.Char("First Name")
	lname = fields.Char("Last Name")
	visitor_email = fields.Char("Email")
	hvisit = fields.Char("Visitor ID")
	hstreet = fields.Char("Street")
	hstreet2 = fields.Char("Street2")
	hcity = fields.Char("City")
	hzip = fields.Char("Zip")
	hphone = fields.Char("Phone")
	hmobile = fields.Char("Mobile")
 
	#EN ESTE METODO SE OBTIENE LOS REGISTROS CON EL CHECK ACTIVO, RECORRO LA VISTA Y CREO EN CLIENTES EL REGITRO SELECCIONADO
	def create_customer(self):
		active_ids = self._context.get('active_ids', []) or []
		for record in self.env['muki.rest'].browse(active_ids):
			self.env["res.partner"].create({'name':record.nombre,'visitor':record.hvisit,'street':record.hstreet,'street2':record.hstreet2,'city':record.hcity,'zip':record.hzip,'email':record.visitor_email})

		# ESTA PROPIEDAD PERMITE ELIMINAR TODOS LOS REGISTROS LUEGO DE HACER EL CREATE
		record_set = self.env['muki.rest'].search([])
		record_set.unlink()

		#ESTA OPCION ES PARA MOSTRAR MENSAJE LUEGO DEL CREATE
		# message_id = self.env['message.wizard'].create({'message': _("Customer successfully created!")})
		return {
			'name': _('Successfull'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'message.wizard',
			# pass the id
			# 'res_id': message_id.id,
			'target': 'new'
		}
		
		
		
class MessageWizard(models.TransientModel):
	_name = 'message.wizard'
	_description = 'Display a message after create customers'

	@api.multi
	def action_ok(self):
		""" close wizard"""	
		return {'type': 'ir.actions.act_window_close'}
