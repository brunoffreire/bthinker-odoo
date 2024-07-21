# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests
import base64
import uuid
import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class porta(models.Model):
	_name = "bthinker.porta"
	_description = "Porta"

	_sql_constraints = [
		('porta_guid_unique', 
		'UNIQUE (guid)', 
		'Código GUID já utilizado.')
		] 
	
	contrato_id = fields.Many2one('bthinker.contrato',  string="Contrato Vinculado", required=True)
	nome = fields.Char(string="Nome", required=True)
	guid = fields.Char(string="GUID", required=True)
	tipo_comunicacao = fields.Selection([
		('tcp', 'TCP/IP'),
		('serial', 'Serial'),
	], string="Tipo de Comunicação", default='serial', required=True)

	firmware_file = fields.Binary(string="Firmware")
	usuario_ids = fields.Many2many("bthinker.usuario", string="Usuários da Porta")
    
	def name_get(self):
		result = []
		for record in self:
			name = "{}".format(record.nome)
			result.append((record.id, name))
		return result
	
	@api.model
	def default_get(self, fields_list):
		uuid1 = uuid.uuid1().hex.upper()
		uuid4 = uuid.uuid4().hex.upper()
		res = super(porta, self).default_get(fields_list)		
		res.update({'guid': uuid1+uuid4})
		return res
	
	
	def action_fire_firmware_update(self):
		server_url = self.env['ir.config_parameter'].sudo().get_param('bthinker_qrdoor.door_server_url')
		for rec in self:
			url = 'http://%s/updateFirmware' % server_url # URL do servidor externo
			headers = {
				'Content-Type': 'application/json',
			}
			
			byte_array = base64.b64decode(rec.firmware_file.decode('utf-8'))
			payload = {
				'door': rec.guid,
				'data': byte_array.hex().upper()
			}

			response = requests.post(url, json=payload, headers=headers)
			response.raise_for_status()  
			response_data = response.json() 
			return response_data