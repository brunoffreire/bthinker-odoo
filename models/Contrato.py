# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class contrato(models.Model):
	_name = "bthinker.contrato"
	_description = "Contrato de Serviço"
	
	nome = fields.Char(string="Nome do Contrato", compute="compute_nome")
	partner_id  = fields.Many2one("res.partner", string="Cliente", required=True)	
	usuario_ids = fields.Many2many("bthinker.usuario", string="Usuários do Contrato")	
	porta_ids = fields.One2many("bthinker.porta", "contrato_id", string="Portas do Contrato")
	state = fields.Selection([
		('inactive', 'Inativo'),
		('active', 'Ativo'),
	], string="Status do Contrato", default='inactive')
	
	def name_get(self):
		result = []
		for record in self:
			name = "{}".format(record.partner_id.name)
			result.append((record.id, name))
		return result
	
	def compute_nome(self):
		for rec in self:
			rec.nome = rec.partner_id.name