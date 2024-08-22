# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import uuid
import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class chave(models.Model):
	_name = "bthinker.camera"
	_description = "Câmera"

	_sql_constraints = [
		('chave_guid_unique', 
		'UNIQUE (guid)', 
		'Código GUID já utilizado.')
		] 
		
	nome = fields.Char(string="Nome da Câmera", required=True)
	guid = fields.Char(string="GUID", required=True)
	contrato_id = fields.Many2one('bthinker.contrato',  string="Contrato Vinculado", required=True)
	porta_ids = fields.Many2many("bthinker.porta", string="Portas da Câmera", domain="[('contrato_id', '=', contrato_id)]")
	usuario_ids = fields.Many2many("bthinker.usuario", string="Usuários com Acesso à Câmera")
	
	
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
		res = super(chave, self).default_get(fields_list)		
		res.update({'guid': uuid1+uuid4})
		return res
	