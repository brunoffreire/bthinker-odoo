# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from asyncio.log import logger
from collections import OrderedDict
from operator import itemgetter

from odoo.addons.bthinker_qrdoor.util.StringUtils import StringUtils
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError, MissingError
from odoo.http import request
from odoo import modules, tools
from dateutil import parser
from datetime import datetime

import datetime
import json
import logging
import requests


_logger = logging.getLogger(__name__)

# Rotas da interface responsiva para acesso web em smartphones
class HttpPublicoController(http.Controller):

	# Metodo para renderizar a página somente se o usuário já fez login
	def checkSession(self):
		env = http.request.env
		if 'user_id' in request.session:
			if request.session['user_id']:				
				user = env["bthinker.usuario"].sudo().search([('id', '=', request.session['user_id'])])
				if user:
					return True

		return False


	
	# Pagina inicial. Verifica se tem dados de login armazenados no dispositivo
	@http.route(['/virtualkey'], type='http', auth="public", website=True)
	def portal_login_by_hash(self, token=None, **kw):				
		values = {}
		if self.checkSession():
			return request.render("bthinker_qrdoor.portal_index", values)
		else:			
			return request.render("bthinker_qrdoor.portal_login_by_hash", values)
	

	
	@http.route('/virtualkey/index', type='http', auth="public", website=True)
	def portal_index(self, token=None, **kw):		

		if not self.checkSession():
			return request.render("bthinker_qrdoor.portal_login", values)	

		# Usuário está logado. Lista as portas dos contratos na pagina
		env = http.request.env
		user = env["bthinker.usuario"].sudo().search([('id', '=', request.session['user_id'])])
		contrato_ids = user.contrato_ids
		values = {
			'contrato_ids': contrato_ids
		}
		return request.render("bthinker_qrdoor.portal_index", values)


	@http.route(['/virtualkey/login'], type='http', auth="public", website=True)
	def portal_login(self, token=None, **kw):
		#env = http.request.env
		#callback_url = http.request.httprequest.host_url		
		values = {}
		return request.render("bthinker_qrdoor.portal_login", values)	

	
	@http.route('/virtualkey/logout', type='http', auth="public", website=True)
	def portal_logout(self, token=None, **kw):
		# Limpando a sessão
		request.session['user_id'] = None
		return request.render("bthinker_qrdoor.portal_login", {})


	@http.route('/virtualkey/cadastro', type='http', auth="public", website=True)
	def portal_cadastro(self, token=None, **kw):
		#env = http.request.env
		#callback_url = http.request.httprequest.host_url

		values = {}
		return request.render("bthinker_qrdoor.portal_cadastro", values)
	

	@http.route('/virtualkey/visita', type='http', auth="public", website=True)
	def portal_cadastro(self, token=None, **kw):
		#env = http.request.env
		#callback_url = http.request.httprequest.host_url

		values = {}
		return request.render("bthinker_qrdoor.portal_visita", values)


	@http.route('/virtualkey/validate', type='http', auth="public", website=True)
	def portal_validate(self, token=None, **kw):
		errno = 0
		message = "Sua conta foi verificada com sucesso!"

		try:
			env = http.request.env
			#callback_url = http.request.httprequest.host_url
			params = http.request.params
			code = params.get('code')
			strJson = StringUtils.fromBase64(code)
			data = StringUtils.jsonToDict(strJson)

			user = env['bthinker.usuario'].sudo().search([('username', '=', data['username']), ('hash_validacao', '=', data['hash'])])
			if not user:
				errno = 1
				message = "Sua conta não foi encontrada."
			
			#cria a chave do usuário
			key = env['bthinker.chave'].sudo().create({'tipo':'user', 'usuario_id':user.id})
			user.write({'state':'checked', 'chave_id': key.id});
					
		except Exception as e:
			errno = 1
			message = e
		
		login_url = env['ir.config_parameter'].get_param('web.base.url', '') + "/virtualkey/login"
		values = {
			'errno' : errno,		
			'message': message,
			'login_url': login_url
		}
		return request.render("bthinker_qrdoor.portal_validate", values)
	

	# ####################################################################
	# Aqui já temos os métodos REST que serão chamados pelas páginas
	# com dados do usuário numa string formato json, para facilitar
	# ####################################################################
	@http.route('/virtualkey/<string:endpoint>', type='json', auth='public', csrf=False, cors='*')
	def portal_request(self, endpoint, **kw):

		env = http.request.env
		url = http.request.httprequest.url
		data = json.loads(http.request.httprequest.data)

		_logger.info("ENDPOINT: %s" % endpoint)
		_logger.info("DATA: %s" % data)

		response = getattr(self, endpoint)(env, data)
		_logger.info("Result: %s" % response)
		return response

	# Método que processa requisição de Login do usuário
	# Após o login bem sucedido, retonarmos um token para o navegador do usuário
	def do_user_login(self, env, data):
		
		try:
			if 'username' not in data:
				return {'errno': 1, 'message': 'Nome do usuário não informado.'}

			if len(data["username"].strip()) <= 0:
				return {'errno': 1, 'message': 'Nome do usuário não pode ser vazio.'}

			if 'senha' not in data:
				return {'errno': 1, 'message': 'Senha não informada.'}

			if len(data["senha"].strip()) <= 0:
				return {'errno': 1, 'message': 'Senha não pode ser vazio.'}

			senha = StringUtils.str2md5(data['senha'])
			user = env['bthinker.usuario'].sudo().search([('username', '=', data['username']), ('senha', '=', senha)])
			if not user:
				return {'errno': 1, 'message': 'Usuário não encontrado ou senha incorreta.'}
			
			if user.state == "unchecked":
				return {'errno': 1, 'message': 'Essa conta ainda não foi ativada. Um link de ativação foi enviado para o e-mail informado durante o cadastro.'}
			
			http.request.session['user_id'] = user.id
			key = user.chave_id.guid
			return {'errno': 0, 'user': user.username, 'hash': user.hash_validacao, 'key':key}			
		
		except AccessDenied:
			return {'errno': 1, 'message': 'Acesso negado.'}
		

	
	# Método que processa requisição de Login do usuário via hash unico
	def do_hash_login(self, env, data):
		
		try:
			if 'user' not in data:
				return {'errno': 1, 'message': 'Nome do usuário não informado.'}

			if len(data["user"].strip()) <= 0:
				return {'errno': 1, 'message': 'Nome do usuário não pode ser vazio.'}

			if 'hash' not in data:
				return {'errno': 1, 'message': 'Hash não informada.'}

			if len(data["hash"].strip()) <= 0:
				return {'errno': 1, 'message': 'Hash não pode ser vazio.'}
			
			if 'key' not in data:
				return {'errno': 1, 'message': 'Key não informada.'}

			if len(data["key"].strip()) <= 0:
				return {'errno': 1, 'message': 'Key não pode ser vazio.'}
			
			user = env['bthinker.usuario'].sudo().search([('username', '=', data['user']), ('hash_validacao', '=', data['hash'])])
			if not user:
				return {'errno': 1, 'message': 'Usuário não encontrado ou hash incorreta.'}
			
			if user.state == "unchecked":
				return {'errno': 1, 'message': 'Essa conta ainda não foi ativada. Um link de ativação foi enviado para o e-mail informado durante o cadastro.'}
			
			if not user.chave_id:
				return {'errno': 1, 'message': 'Não há chave definida para esse usuário.'}
			
			if user.chave_id.guid != data['key']:
				return {'errno': 1, 'message': 'Chave incorreta.'}
						
			http.request.session['user_id'] = user.id			
			return {'errno': 0, 'message' : 'Login por hash bem sucedido.'}
		
		except AccessDenied:
			return {'errno': 1, 'message': 'Acesso negado.'}
		
		
	
	# Salvar cadastro de novo usuário
	def check_username_profile(self, env, data):		
		valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789._-"
		username = data['username']

		if len(username.strip()) <= 0:
			return {'errno': '1', 'message': "Nome de usuário não pode ser vazio."}	
		
		for c in username:
			if c.lower() not in valid_chars:
				return {'errno': '1', 'message': "Nome de usuário pode conter apenas letras, números, e os caracteres '.', '-' e '_'."}	
    		
		user = env['bthinker.usuario'].sudo().search([('username', '=', username)])
		if user:
			return {'errno': '1', 'message': "Nome de usuário '%s' indisponível." % username}
	
		return {'errno': '0', 'message': "Nome de usuário '%s' está disponível." % username}

	
	# Salvar cadastro de novo usuário
	def save_user_profile(self, env, data):
		try:
			fields_to_check = {
				'username': 'Nome de Usuário',
				'nome': 'Nome',
				'email': 'E-Mail',
				'celular': 'Celular',
				'senha': 'Senha',
				'confirma_senha': 'Confirmação de Senha'
			}

			# Verificando campos preenchidos
			for key, value in fields_to_check.items():
				if key not in data:
					return {'errno': 1, 'message': 'Parametro %s não informado.' % (value)}

				if len(data[key].strip()) <= 0:
					return {'errno': 1, 'message': 'Campo %s não pode ser vazio.' % (value)}

			# Verificando senhas iguais
			if data['senha'] != data['confirma_senha']:
				return {'errno': 1, 'message': 'Senha e Confirmação de Senha devem ser iguais.'}

			if data['termo'] != '1':
				return {'errno': 1, 'message': 'É necessário concordar com os termos de uso.'}
			

			valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789._-"
			username = data['username']

			if len(username.strip()) <= 0:
				return {'errno': '1', 'message': "Nome de usuário não pode ser vazio."}	
			
			for c in username:
				if c.lower() not in valid_chars:
					return {'errno': '1', 'message': "Nome de usuário pode conter apenas letras, números, e os caracteres '.', '-' e '_'."}	
				
			user = env['bthinker.usuario'].sudo().search([('username', '=', username)])
			if user:
				return {'errno': '1', 'message': "Nome de usuário '%s' indisponível." % username}

			# Criando usuário na base
			vals = {
				'username': data['username'],
				'nome': data['nome'],
				'email': data['email'],
				'celular': data['celular'],
				'senha': data['senha'],
			}
												
			user = env["bthinker.usuario"].sudo().create(vals)
			user.send_enroll_mail()
			return {'errno': 0, 'message': 'Dados salvos com sucesso!'}
	
		except Exception as err:
			return {'errno': 500, 'message': err}
	

	# Cria uma nova visita
	def save_new_visit(self, env, data):
		try:
			if 'nome_visitante' not in data:
				return {'errno': 1, 'message': 'Nome do visitante não informado.'}

			if len(data["nome_visitante"].strip()) <= 0:
				return {'errno': 1, 'message': 'Nome do visitante não pode ser vazio.'}

			if 'duracao' not in data:
				return {'errno': 1, 'message': 'Duração não informada.'}

			if len(data["duracao"].strip()) <= 0:
				return {'errno': 1, 'message': 'Duração não pode ser vazio.'}
			
			try:
				duracao = int(data["duracao"])
				if duracao < 1 or duracao > 24:
					return {'errno': 1, 'message': 'Duração deve ser um valor numérico positivo entre 1 e 24.'}	
			except ValueError:
				return {'errno': 1, 'message': 'Duração deve ser um valor numérico positivo entre 1 e 24.'}
			
			if 'usa_uma_vez' not in data:
				return {'errno': 1, 'message': 'Limite de utilização não informado.'}
			
			# Criando usuário na base
			chave = env['bthinker.chave'].sudo().create({'tipo':'visitor'})

			user_id = http.request.session['user_id']
			vals = {
				'usuario_id': user_id,
				'nome_visitante': data['nome_visitante'],
				'duracao': data['duracao'],
				'usa_uma_vez': data['usa_uma_vez'],
				'chave_id': chave.id,
				'executado': False,
				'finalizado': False
			}
												
			visita = env["bthinker.visita"].sudo().create(vals)					
			chave.write({'visita_id': visita.id});
			
			url = http.request.httprequest.host_url.replace("http:", "https:")
			if url.endswith('/'):
				url = url[:-1]

			url = "%s/virtualkey/visita?key=%s" % (url, chave.guid)

			_logger.info("URL VISITA: %s" % url)

			return {'errno': 0, 'visitor':visita.nome_visitante.upper(), 'user': visita.usuario_id.nome.upper(), 'url': url}
		
		except ex:
			return {'errno': 1, 'message': 'Acesso negado.'}

	
	
	def open_door_by_pin(self, env, data):
		data['require_pin'] = True
		return self.auth_key_door(env, data)
	
	
	def auth_key_door(self, env, data):
		_logger.info("auth_key_door: %s" % data)
		try:
			if 'key' not in data:
				return {'errno': 1, 'message': 'Chave não informada.'}

			if len(data["key"].strip()) <= 0:
				return {'errno': 1, 'message': 'Chave não pode ser vazio.'}

			if 'door' not in data:
				return {'errno': 1, 'message': 'Porta não informada.'}

			if len(data["door"].strip()) <= 0:
				return {'errno': 1, 'message': 'Porta não pode ser vazio.'}
			
			# tratamento para solicitação de abertura remota
			if 'require_pin' in data:
				if 'pin' not in data:
					return {'errno': 1, 'message': 'PIN não informado.'}

				if len(data["pin"].strip()) <= 0:
					return {'errno': 1, 'message': 'PIN não pode ser vazio.'}
							

			porta = env['bthinker.porta'].sudo().search([('guid', '=', data['door'])])
			if not porta:
				return {'errno': '1', 'message': "Porta não identificada no sistema."}
			
			chave = env['bthinker.chave'].sudo().search([('guid', '=', data['key'])])
			if not chave:
				return {'errno': '1', 'message': "Chave não identificada no sistema."}
						
			# Tudo certo com a porta?
			# Contrato ativo?
			if not porta.contrato_id:
				return {'errno': '1', 'message': "Porta não vinculada a uma conta de cliente."}
			
			if not porta.contrato_id.state == 'inactive':
				return {'errno': '1', 'message': "Porta vinculada a uma conta inativa."}


			# Verificando a permissão do usuário na porta
			# Seje o usuário requisitando ou um de seus visitantes
			usuario = None
			if chave.visita_id:
				
				# tratamento para solicitação de abertura remota
				if 'require_pin' in data:
					return {'errno': '1', 'message': "Não é permitida abertura remota em visitas."}

				if chave.visita_id.usuario_id:
					usuario = chave.visita_id.usuario_id

				current_time = datetime.datetime.now()
				limit_time = chave.visita_id.create_date + datetime.timedelta(hours=chave.visita_id.duracao)

				if current_time > limit_time:
					chave.visita_id.write({'finalizado':True})
					return {'errno': '1', 'message': "Horário para visita já encerrado."}

			elif chave.usuario_id:
				usuario = chave.usuario_id
				
				# tratamento para solicitação de abertura remota
				if 'require_pin' in data:
					if usuario.pin_abertura != int(data['pin']):
						return {'errno': '1', 'message': "PIN de abertura remota incorreto."}

			# o que une porta e usuário é o contrato
			contrato = usuario.contrato_ids.search([('id', '=', porta.contrato_id.id)])
			if not contrato:
				return {'errno': '1', 'message': "Usuário requisitante ou criador da visita não tem acesso a porta solicitada."}
			

			# se é chave de visita
			#if chave.visita_id:				
			#	chave.visita_id.write({'executado':True, 'finalizado': chave.visita_id.usa_uma_vez})
				
			
			#if chave.usuario_id:
				# grava acesso
							
			data = self.call_esp_server(porta.guid)			
			_logger.info("ESP DATA: %s" % data)

			if data['errno'] != "0":
				return {'errno': data['errno'], 'message': data['message']}
			
			return {'errno': '0', 'message': "Acesso liberado."}

		except ex:
			return {'errno': 1, 'message': ex}	
	


	def call_esp_server(self, porta_guid):
		url = 'http://localhost:8200/qrdoor/openDoor'  # URL do servidor externo
		headers = {
			'Content-Type': 'application/json',
		}
		
		payload = {
			'door': porta_guid,
		}
		response = requests.post(url, json=payload, headers=headers)
		response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
		response_data = response.json()  # Processa a resposta JSON
		return response_data
		