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
import datetime
import json
import logging
import base64
import ast



_logger = logging.getLogger(__name__)

# Rotas da interface responsiva para acesso web em smartphones
class HttpPublicoController(http.Controller):

	# Metodo para renderizar a página somente se o usuário já fez login
	def render(self, template, values={}):
		env = http.request.env

		if 'user_id' in request.session:
			if request.session['user_id']:				
				user = env["bthinker.usuario"].sudo().search([('id', '=', request.session['user_id'])])

				if user:
					values['usuario'] = user

				return request.render(template, values)

		return request.render("bthinker_qrdoor.portal_login", values)
		# return request.redirect('/virtualkey/login')

	@http.route(['/virtualkey', '/virtualkey/login'], type='http', auth="public", website=True)
	def portal_login(self, token=None, **kw):
		env = http.request.env
		callback_url = http.request.httprequest.host_url
		values = {
			# 'page_name': 'ticket-login',
			# 'callback_url' : callback_url,
			# 'share_link_code': token
		}
		return self.render("bthinker_qrdoor.portal_login", values)

	@http.route('/virtualkey/index', type='http', auth="public", website=True)
	def portal_index(self, token=None, **kw):

		env = http.request.env
		callback_url = http.request.httprequest.host_url
		values = {
			# 'page_name': 'ticket-login',
			# 'callback_url' : callback_url,
			# 'share_link_code': token
		}

		return self.render("bthinker_qrdoor.portal_index", values)

	@http.route('/virtualkey/logout', type='http', auth="public", website=True)
	def portal_logout(self, token=None, **kw):
		# Limpando a sessão
		request.session['user_id'] = None
		return request.render("bthinker_qrdoor.portal_login", {})


	@http.route('/virtualkey/cadastro', type='http', auth="public", website=True)
	def portal_cadastro(self, token=None, **kw):
		env = http.request.env
		callback_url = http.request.httprequest.host_url

		values = {
			# 'page_name': 'ticket-login',
			# 'callback_url' : callback_url,
			# 'share_link_code': token
		}

		return request.render("bthinker_qrdoor.portal_cadastro", values)


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


	@http.route('/virtualkey/profile', type='http', auth="public", website=True)
	def portal_profile(self, token=None, **kw):
		env = http.request.env
		callback_url = http.request.httprequest.host_url
		values = {
			# 'page_name': 'ticket-login',
			# 'callback_url' : callback_url,
			# 'share_link_code': token
		}

		return self.render("bthinker_qrdoor.portal_profile", values)

	@http.route('/virtualkey/visit', type='http', auth="public", website=True)
	def portal_visit(self, token=None, **kw):

		env = http.request.env
		callback_url = http.request.httprequest.host_url
		# purposes = env["bthinker_qrdoor.visit_purpose"].sudo().search([], order="name")

		values = {
			# 'page_name': 'ticket-login',
			# 'callback_url' : callback_url,
			# 'share_link_code': token
			# 'purposes':purposes
		}

		return self.render("bthinker_qrdoor.portal_visit", values)

	
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

	def get_token_as_json(self, token):		
		key = bytearray.fromhex(token)		
		return json.loads(key)

	# Método que processa requisição de Login do usuário
	# Após o login bem sucedido, retonarmos um token para o navegador do usuário
	# com dados do usuário numa string formato json, para facilitar processamento
	# nas funções que precisarem usar informações ndo token
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
			key = ""
			return {'errno': 0, 'user': user.username, 'hash': user.auto_login_hash, 'key':key}			
		
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
				'name': 'Nome',
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

			if data['agree'] != '1':
				return {'errno': 1, 'message': 'É necessário concordar com os termos de uso.'}

			# Criando usuário na base
			vals = {
				'username': data['username'],
				'nome': data['name'],
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
			env = http.request.env

			if 'user_id' in request.session:
				if request.session['user_id']:

					users = env["res.users"].sudo().search([
						('id', '=', request.session['user_id']),
					], order="id")

					if users:
						host_id = users[0].partner_id.id
						data['host_id'] = host_id

			fields_to_check = {
				'visitor': 'Visitante',
				'portal_level_visitor': 'Permissão de Acesso',
				'check-in': 'Data de Entrada',
				'check-out': 'Data de Saída',
				'visit_reason':'Motivo da Visita'
			}

			# Verifica se possui veiculo
			#if data['have_car'] == True:
			#	...

			# Verificando campos preenchidos
			
			for key, value in fields_to_check.items():
				if key not in data:
					return {'result': 'ERROR', 'errno': 1, 'message': 'Parametro %s não informado.' % (value)}

				if len(data[key]) <= 0:
					return {'result': 'ERROR', 'errno': 2, 'message': 'Campo %s não pode ser vazio.' % (value)}

			datetime_in = parser.parse(data['check-in'])
			datetime_out = parser.parse(data['check-out'])

			# Verifica conflitos de data
			if datetime_in >= datetime_out:
				return {'result': 'ERROR', 'errno': 2, 'message': 'Data de entrada não pode ser menor ou igual a Data de saída.'}


			#tratando o array de ID de visitantes, lembrar-se de alterar o campo no front-end para aceitar multiple
			#alterar para que a cada iteração com visitor um novo registro seja enviado para o banco (acrescentar dentro do for abaixo)
			for visitor in data['visitor']:
				visitor_id = visitor
			##	

			vals = {
				'visitor': visitor_id,
				'check_in': datetime_in,
				'check_out': datetime_out,
				'qty_entries': data['multiple_acess']
			}

			# ATENCAO: Isso ja cria a visita. Devemos apenas atualizar a visita.
			visit = env['bthinker_qrdoor.visit'].sudo().create(vals)

			# Adiciona o o motivo da visita a visita
			
			for reason in data['visit_reason']:
				teste = reason
				_logger.info(teste.isdigit())
				if teste.isdigit():
					vals = {
						'purpose': [(4, reason)]
					}
				else:
					last_id = env['bthinker_qrdoor.visit_purpose'].search([])[-1].id	
					vals = {
					'purpose': [(4, last_id)]
				}
				
				_logger.info('chegou aqui')
				visit.write(vals)

				# Adiciona a regra de acesso a visita
			for level_access in data['portal_level_visitor']:
				vals = {
					'accessrule_ids': [(4, level_access)]

				}
				visit.write(vals)

				# Adiciona o cartão a visita
			for card_id in data['card_number_visitor']:
				vals = {
					'accesscard_ids': [(1, card_id, {'visit_id': visit.id})]

				}
				visit.write(vals)

			return {'result': 'OK', 'errno': 0, 'message': 'Dados salvos com sucesso!'}

		except Exception as err:
			return {'result': 'ERROR', 'errno': 500, 'message': err}

	# Pega as informações de um visitante cadastro para apresentar na tabela
	def get_my_visitor(self, env, data):
		try:
			env = http.request.env
			
			visitor_vals = []
			
		
			user_id = request.session['user_id']
			user_partner = env['res.users'].sudo().search([('id', '=', user_id)])
			visitors = env['res.partner'].sudo().search(
				[('create_uid', '=', user_partner.id), ('accesstype_id', '=', 3)], order='id')
			for visitor in visitors:
				visitor_vals.append({
					'visitor_id': visitor.id,
					'visitor_name': visitor.name,
					'visitor_photo': visitor.bio_photo
				})

			return {'result': 'OK', 'errno': 0, 'message': 'Consulta Realizada', 'visitors': visitor_vals}

		except Exception as err:
			return {'result': 'ERROR', 'errno': 500, 'message': err}

	# Pega as informações de uma visita cadastrada para apresentar na tabela
	def get_my_visit(self, env, data):
		try:
			env = http.request.env

			visits_vals = []
			
			user_id = request.session['user_id']
			
			visits = env['bthinker_qrdoor.visit'].sudo().search([('create_uid', '=', user_id)], order='id')
			_logger.info(visits)
			for visit in visits:
				_logger.info(visit.visitor)
				_logger.info(visit.visitor.id)
				
				visitor_id = env['res.partner'].sudo().search([('id', '=', visit.visitor.id),('create_uid', '=', user_id)], order='id')
				visits_vals.append({
					'visit_name': visitor_id.name,
					'visit_check_in': visit.check_in,
					'visit_check_out': visit.check_out,
					'visit_id': visit.id

				})
			return {'result': 'OK', 'errno': 0, 'message': 'Consulta Realizada', 'visits': visits_vals}
		except Exception as err:

			return {'result': 'ERROR', 'errno': 500, 'message': err}

	# Pega as informações de um visitante cadastrado para apresentar no form de edição
	def get_info_visitor(self, env, data):

		try:
			env = http.request.env
			visitor_vals = []

			visitor = env['res.partner'].sudo().search(
				[('id', '=', data['id'])], order='id')

			visitor_vals.append({
				'visitor_name': visitor.name,
				'visitor_photo': visitor.bio_photo,
				'visitor_email': visitor.email,
				'visitor_phone': visitor.mobile,
				'visitor_id' : visitor.id
			})
			_logger.info(visitor_vals)

			return {'result': 'OK', 'errno': 0, 'message': 'Consulta Realizada', 'visitor': visitor_vals}

		except Exception as err:
			return {'result': 'ERROR', 'errno': 500, 'message': err}

	# Pega as informações de uma visita cadastrada para apresentar no form de edição
	def get_info_visit(self, env, data):

		try:
			env = http.request.env
			visit_vals = []

			visit = env['bthinker_qrdoor.visit'].sudo().search(
				[('id', '=', data['id'])], order='id')
			visitor_id = env['res.partner'].sudo().search(
					[('id', '=', visit.visitor.id)], order='id')
			visit_vals.append({
				'visit_name': visitor_id.name,
				'visit_id': visit.id,
				'visit_host': visit.main_host_id,
				'visit_multiple_access': visit.qty_entries,
				'visit_check_in': visit.check_in,
				'visit_check_out': visit.check_out
			})

			return {'result': 'OK', 'errno': 0, 'message': 'Consulta Realizada', 'visit': visit_vals}

		except Exception as err:
			return {'result': 'ERROR', 'errno': 500, 'message': 'Erro ao realizar consulta'}

	def get_card_qrcode(self, env, data):
		try:
			qrCode = QRCode()
			user_id = request.session['user_id']
			user = env['res.users'].sudo().search([('id', '=', user_id)])
			
			cards = env['bthinker_qrdoor.accesscard'].sudo().search([('partner_id', '=', user.partner_id.id)])

			qrcodeData = []
			for card in cards:
				qrcodeData.append({
					'card_number' : card.name,
					'card_qrcode' : qrCode.get_base64(str(card.name))
				})
			

			return {'result' : 'OK', 'errno': 0, 'message': 'QRcode gerado', 'data': qrcodeData }
		except Exception as err:
			return {'result': 'ERRO', 'errno': 500, 'message': f'Erro ao realizar consulta: {err}'}