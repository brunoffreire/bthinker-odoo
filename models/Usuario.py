# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.bthinker_qrdoor.util.StringUtils import StringUtils

import uuid
import hashlib
import logging
_logger = logging.getLogger(__name__) 

# Uma área de acesso representa um local físico terá o seu acesso controlado pelo sistema
# através de portas e equipamentos a ela associados.
class usuario(models.Model):
	_name = "bthinker.usuario"
	_description = "Usuário do Serviço"

	_sql_constraints = [
		('chave_username_unique', 
		'UNIQUE (username)', 
		'Nome de usuário não disponível.')
		]
			
	nome = fields.Char(string="Nome Completo")
	username = fields.Char(string="Nome de usuário")
	senha = fields.Char(string="Senha")
	auto_login_hash = fields.Char(string="Hash para login automático")
	email = fields.Char(string="E-mail")
	celular = fields.Char(string="Celular")	
	state = fields.Selection([
		('unchecked', 'Não Verificado'),
		('checked', 'Verificado'),
	], string="Status da Conta", tracking=True, default='unchecked')

	hash_validacao = fields.Char(string="Hash para validação de e-mail")
	link_validacao = fields.Char(string='Link de validação', compute='compute_link')
	chave_id = fields.Many2one("bthinker.chave", string="Chave", ondelete="set null", readonly=True)

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
		res = super(usuario, self).default_get(fields_list)		
		res.update({'hash_validacao': uuid1+uuid4})
		return res

	@api.model
	def create(self, vals):		
		if 'senha' in vals:
			vals['senha'] = StringUtils.str2md5(vals['senha'])

		rec = super(usuario, self).create(vals)		
		return rec
	

	def write(self, vals):
		if 'senha' in vals:
			vals['senha'] = StringUtils.str2md5(vals['senha'])

		rec = super(usuario, self).write(vals)		
		return rec
	
	
	@api.depends('hash_validacao')
	def compute_link(self):
		for rec in self:
			data = {'username':rec.username, 'hash': rec.hash_validacao}
			strJson = StringUtils.dictToJson(data)
			code = StringUtils.toBase64(strJson)
			
			url = self.env['ir.config_parameter'].get_param('web.base.url', '')
			rec.link_validacao = url + "/virtualkey/validate?code=" + code

	def action_send_enroll_mail(self):
		template = self.env.ref('bthinker_qrdoor.user_enroll_mail_template')
		template.send_mail(self.id, force_send=True)

	def send_enroll_mail(self):
		template = self.env.ref('bthinker_qrdoor.user_enroll_mail_template')
		template.send_mail(self.id, force_send=False)

	def validate_account(self):
		
		uuid1 = uuid.uuid1().hex.upper()
		uuid4 = uuid.uuid4().hex.upper()
		
		self.env['bthinker.chave'].create({
				'usuario_id' : id, 
				'nome' : ('Grupo %s' % id),
				'guid': 1
				})