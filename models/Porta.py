# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
	
	@api.model
	def default_get(self, fields_list):
		uuid1 = uuid.uuid1().hex.upper()
		uuid4 = uuid.uuid4().hex.upper()
		res = super(porta, self).default_get(fields_list)		
		res.update({'guid': uuid1+uuid4})
		return res