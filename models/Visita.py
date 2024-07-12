# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class visita(models.Model):
	_name = "bthinker.visita"
	_description = "Visita"
	
	usuario_id = fields.Many2one('bthinker.usuario',  string="Criado por", required=True)
	nome_visitante = fields.Char(string="Visitante", required=True)
	duracao = fields.Integer(string="Duração", required=True)
	usa_uma_vez = fields.Boolean(string="Expira após uso", help="Marcando essa opção, a chave será invalidada assim que utilizada.")
	chave_id  = fields.Many2one("bthinker.chave", string="Chave Associada", required=True, ondelete="cascade")
	
	executado = fields.Boolean(string="Expira após uso", help="Indica que a visita foi realizada.", required=True, default=False)
	finalizado = fields.Boolean(string="Encerrada", help="Indica que a visita está finalizada.", required=True, default=False)