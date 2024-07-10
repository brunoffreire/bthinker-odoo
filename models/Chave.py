# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import uuid
import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class chave(models.Model):
	_name = "bthinker.chave"
	_description = "Chave Virtual"

	_sql_constraints = [
		('chave_guid_unique', 
		'UNIQUE (guid)', 
		'Código GUID já utilizado.')
		] 
		
	nome = fields.Char(string="Nome da Chave", compute="compute_nome")
	guid = fields.Char(string="GUID", required=True)
	tipo = fields.Selection([
		('user', 'Chave de Usuário'),
		('visitor', 'Chave de Visita'),
	], string="Status da Conta", default='user', required=True)

	usuario_id = fields.Many2one("bthinker.usuario", string="Usuário", ondelete="set null")
	visita_id = fields.Many2one("bthinker.visita", string="Visita", ondelete="set null")
	
	
	@api.model
	def default_get(self, fields_list):
		uuid1 = uuid.uuid1().hex.upper()
		uuid4 = uuid.uuid4().hex.upper()
		res = super(chave, self).default_get(fields_list)		
		res.update({'guid': uuid1+uuid4})
		return res
	
	def compute_nome(self):
		for record in self:
			url = self.env['ir.config_parameter'].get_param('web.base.url', '')
			record.link_validacao = url + "/?code=" + record.hash_validacao
	