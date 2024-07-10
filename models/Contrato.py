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
	
	partner_id  = fields.Many2one("res.partner", string="Cliente", required=True)	
	usuario_ids = fields.Many2many("res.partner", string="Usuários vinculados a este contrato",  domain="[('is_company', '=', False)]")	
	porta_ids = fields.One2many("bthinker.porta", "contrato_id", string="Portas do Contrato")
	state = fields.Selection([
		('inactive', 'Inativo'),
		('active', 'Ativo'),
	], string="Status do Contrato", tracking=True, default='inactive')