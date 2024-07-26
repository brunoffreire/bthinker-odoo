# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import uuid
import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class chave(models.Model):
	_name = "bthinker.registro_acesso"
	_description = "Registro de Acesso"

	# Nome do usuário ou do visitante
	nome_pessoa = fields.Char(string="Nome da Pessoa", required=True, readonly=True)		
	usuario_id = fields.Many2one("bthinker.usuario", string="Usuário", ondelete="set null", readonly=True)
	porta_id = fields.Many2one("bthinker.porta", string="Porta", ondelete="set null", readonly=True)		
	tipo = fields.Selection([
		('user', 'Usuário'),
		('visitor', 'Visitante')
	], string="Tipo de Acesso", required=True, readonly=True)

	metodo = fields.Selection([
		('qrcode', 'QRCode'),
		('remoto', 'Abertura Remota')
	], string="Método de Acesso", required=True, readonly=True)

	resultado = fields.Selection([
		('sucesso', 'Sucesso'),
		('falha', 'Falha')
	], string="Resultado", required=True, readonly=True)
	
	
	
	def name_get(self):
		result = []
		for record in self:
			name = "Acesso de {}".format(record.nome_pessoa)
			result.append((record.id, name))
		return result