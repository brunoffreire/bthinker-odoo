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
		('usuario_username_unique', 
		'UNIQUE (username)', 
		'Nome de usuário não disponível.'),

		('usuario_auto_login_unique', 
		'UNIQUE (auto_login_hash)', 
		'Hash de login não disponível.')
		]
			
	nome = fields.Char(string="Nome Completo")
	username = fields.Char(string="Nome de usuário")
	senha = fields.Char(string="Senha")
	tipo = fields.Selection([
		('comum', 'Comum'),
		('admin', 'Administrador'),
	], string="Tipo de Usuário", default='comum')

	auto_login_hash = fields.Char(string="Hash para login automático")
	email = fields.Char(string="E-mail")
	celular = fields.Char(string="Celular")	
	state = fields.Selection([
		('unchecked', 'Não Verificado'),
		('checked', 'Verificado'),
	], string="Status da Conta", default='unchecked')

	hash_validacao = fields.Char(string="Hash para validação de e-mail")
	chave_id = fields.Many2one("bthinker.chave", string="Chave", ondelete="set null", readonly=True)	
	contrato_ids = fields.Many2many('bthinker.contrato', string='Contratos')
	status_ultimo_login = fields.Char(string="Status do último Login", readonly=True)	
	porta_ids = fields.Many2many("bthinker.porta", string="Portas do Usuário", domain="[('contrato_id', 'in', contrato_ids)]")

	def name_get(self):
		result = []
		for record in self:
			name = "{}".format(record.nome)
			result.append((record.id, name))
		return result
	

	@api.model
	def create(self, vals):
		
		if 'senha' in vals:
			vals['senha'] = StringUtils.str2md5(vals['senha'])

		# Cria a chave do usuario
		chave = self.env['bthinker.chave'].sudo().create({'tipo':'user'})
		vals['chave_id'] = chave.id

		# Cria usuário e associa a chave ao usuário criado
		rec = super(usuario, self).create(vals)
		chave.write({'usuario_id': rec.id})

		return rec
	

	def write(self, vals):
		if 'senha' in vals:
			vals['senha'] = StringUtils.str2md5(vals['senha'])

		# Salvar os contratos atuais antes da atualização
		contratos_antes = self.contrato_ids
		rec = super(usuario, self).write(vals)
		
		# Verificar se os contratos foram alterados
		if 'contrato_ids' in vals:
		
			# Obter os novos contratos após a atualização
			contratos_depois = self.contrato_ids

			# Encontrar os contratos desassociados
			contratos_removidos = contratos_antes - contratos_depois

			if contratos_removidos:
				# Encontrar as portas que pertencem aos contratos desassociados
				portas_removidas = self.env['bthinker.porta'].search([('contrato_id', 'in', contratos_removidos.ids)])
				
				# Desassociar essas portas do usuário
				self.write({'porta_ids': [(3, porta.id) for porta in portas_removidas]})

		return rec
	
	
	def action_send_enroll_mail(self):
		for rec in self:

			# Cria um novo hash de validação da troca de senha
			uuid1 = uuid.uuid1().hex.upper()
			uuid4 = uuid.uuid4().hex.upper()						
			rec.sudo().write({'hash_validacao': uuid1+uuid4})

			template = self.env.ref('bthinker_qrdoor.base_usuario_mail_template')
			email_values = template.generate_email(rec.id, ['subject', 'body_html',
             'email_from',
             'email_cc', 'email_to', 'partner_to', 'reply_to',
             'auto_delete', 'scheduled_date'])
			

			data = {
				'user' : rec.username,
				'hash' : rec.hash_validacao
			}

			hash = StringUtils.dictToJson(data)
			hash = StringUtils.toBase64(hash)			
			url = self.env['ir.config_parameter'].get_param('web.base.url', '') + "/virtualkey/validate?hash=" + hash			

			email_values['auto_delete'] = False
			email_values['subject'] = "Confirmação de Cadastro"			
			if not email_values['email_from']:
				email_values['email_from'] = template.mail_server_id.smtp_user
			email_values['email_to'] = rec.email
			email_values['body_html'] = '''Olá %s,<br/><br/>
			Para validar o seu cadastro no sistema de portaria, clique no link abaixo:<br/><br/>
			%s
			''' % (rec.nome, url)			
			mail = self.env['mail.mail'].create(email_values)
			mail.send()
            			
	
	def send_password_change_email(self):
		for rec in self:

			# Cria um novo hash de validação da troca de senha
			uuid1 = uuid.uuid1().hex.upper()
			uuid4 = uuid.uuid4().hex.upper()						
			rec.sudo().write({'hash_validacao': uuid1+uuid4})

			template = self.env.ref('bthinker_qrdoor.base_usuario_mail_template')
			email_values = template.generate_email(rec.id, ['subject', 'body_html',
             'email_from',
             'email_cc', 'email_to', 'partner_to', 'reply_to',
             'auto_delete', 'scheduled_date'])
			
			data = {
				'user' : rec.username,
				'hash' : rec.hash_validacao
			}
			
			hash = StringUtils.dictToJson(data)
			hash = StringUtils.toBase64(hash)			
			url = self.env['ir.config_parameter'].get_param('web.base.url', '') + "/virtualkey/mudasenha?hash=" + hash

			email_values['auto_delete'] = False
			email_values['subject'] = "Alteração de Senha"
			if not email_values['email_from']:
				email_values['email_from'] = template.mail_server_id.smtp_user
			email_values['email_to'] = rec.email	
			email_values['body_html'] = '''Olá %s,<br/><br/>
			Para alterar a sua senha no sistema de portaria, clique no link abaixo:<br/><br/>
			%s
			''' % (rec.nome, url)			
			mail = self.env['mail.mail'].create(email_values)
			mail.send()
		

class convite_usuario(models.Model):
	_name = "bthinker.convite_usuario"
	_description = "Convite de Usuário do Serviço"

	_sql_constraints = [
		('convite_usuario_hash_unique', 
		'UNIQUE (guid)', 
		'Hash não disponível.')
		]
	
	usuario_id = fields.Many2one('bthinker.usuario',  string="Criado por", required=True)
	contrato_id = fields.Many2one('bthinker.contrato',  string="Contrato Associado", required=True)
	guid = fields.Char(string="Hash do Convite", required=True)

	@api.model
	def default_get(self, fields_list):
		uuid1 = uuid.uuid1().hex.upper()
		uuid4 = uuid.uuid4().hex.upper()
		res = super(convite_usuario, self).default_get(fields_list)		
		res.update({'guid': uuid1+uuid4})
		return res