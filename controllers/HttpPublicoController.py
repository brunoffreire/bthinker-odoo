# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from asyncio.log import logger
from collections import OrderedDict
from operator import itemgetter

from odoo.addons.bthinker_qrdoor.util.ModelUtils import ModelUtils
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
#env = http.request.env
#callback_url = http.request.httprequest.host_url		

class HttpPublicoController(http.Controller):
		
	@http.route(['/virtualkey', '/virtualkey/index'], type='http', auth="public", website=True)
	def portal_index(self, token=None, **kw):
		values = {}
		return request.render("bthinker_qrdoor.portal_index", values)						


	@http.route('/virtualkey/login', type='http', auth="public", website=True)
	def portal_login(self, token=None, **kw):
		request.session['user'] = None
		values = {}
		return request.render("bthinker_qrdoor.portal_login", values)	


	@http.route('/virtualkey/logout', type='http', auth="public", website=True)
	def portal_logout(self, token=None, **kw):
		request.session['user'] = None
		return request.redirect("/virtualkey/login")
	

	@http.route('/virtualkey/visita', type='http', auth="public", website=True)
	def portal_visita(self, token=None, **kw):
		values = {}
		return request.render("bthinker_qrdoor.portal_visita", values)
	

	@http.route('/virtualkey/cadastro', type='http', auth="public", website=True)
	def portal_cadastro(self, token=None, **kw):
		
		errno = 0
		message = None
		env = http.request.env

		try:	
			params = http.request.params
			guid = params.get('hash')
			convite = env['bthinker.convite_usuario'].sudo().search([('guid', '=', guid)])
			
			if not convite:
				errno = 1
				message = "Convite de cadastro inválido."
								
		except Exception as e:
			errno = 1
			message = e
		
		values = {
			'errno' : errno,		
			'message': message
		}
		return request.render("bthinker_qrdoor.portal_cadastro", values)
	

	@http.route('/virtualkey/mudasenha', type='http', auth="public", website=True)
	def portal_muda_senha(self, token=None, **kw):
		
		errno = 0
		message = None
		env = http.request.env

		try:	
			params = http.request.params
			hash = params.get('hash')		
			strJson = StringUtils.fromBase64(hash)
			data = StringUtils.jsonToDict(strJson)

			user = env['bthinker.usuario'].sudo().search([('username', '=', data['user']), ('hash_validacao', '=', data['hash'])])
			
			if not user:
				errno = 1
				message = "Cadastro de usuário não localizado."
								
		except Exception as e:
			errno = 1
			message = e
		
		values = {
			'errno' : errno,		
			'message': message
		}
		return request.render("bthinker_qrdoor.portal_muda_senha", values)
	


	@http.route('/virtualkey/validate', type='http', auth="public", website=True)
	def portal_validate(self, token=None, **kw):
		
		errno = 0
		message = "Sua conta foi verificada com sucesso!"
		env = http.request.env		

		try:	
			params = http.request.params
			hash = params.get('hash')
			strJson = StringUtils.fromBase64(hash)
			data = StringUtils.jsonToDict(strJson)

			_logger.info("VALIDACAO: %s" % data)

			user = env['bthinker.usuario'].sudo().search([('username', '=', data['user']), ('hash_validacao', '=', data['hash'])])
			if not user:
				errno = 1
				message = "Sua conta não foi encontrada."
			
			user.write({'state':'checked'});
					
		except Exception as e:
			errno = 1
			message = e
		
		#login_url = env['ir.config_parameter'].get_param('web.base.url', '') + "/virtualkey/login"
		values = {
			'errno' : errno,		
			'message': message
		}
		return request.render("bthinker_qrdoor.portal_validate", values)
	

	# ####################################################################
	# Aqui já temos os métodos REST que serão chamados pelas páginas
	# com dados do usuário numa string formato json, para facilitar
	# ####################################################################
	@http.route('/api/<string:endpoint>', type='json', auth='public', csrf=False, cors='*')
	def portal_request(self, endpoint, **kw):

		env = http.request.env
		url = http.request.httprequest.url
		data = json.loads(http.request.httprequest.data)

		_logger.info("URL: %s" % url)
		_logger.info("ENDPOINT: %s" % endpoint)
		_logger.info("DATA: %s" % data)

		response = getattr(self, endpoint)(env, data)
		_logger.info("Result: %s" % response)

		return response

	# Método que processa requisição de Login do usuário
	# Após o login bem sucedido, retonarmos um token para o navegador do usuário
	def do_user_login(self, env, data):
		
		try:
			erro = None
			while True:
				if 'username' not in data:
					erro = {'errno': 1, 'message': 'Nome do usuário não informado.'}
					break

				if len(data["username"].strip()) <= 0:
					erro = {'errno': 1, 'message': 'Nome do usuário não pode ser vazio.'}
					break

				if 'senha' not in data:
					erro = {'errno': 1, 'message': 'Senha não informada.'}
					break

				if len(data["senha"].strip()) <= 0:
					erro = {'errno': 1, 'message': 'Senha não pode ser vazio.'}
					break
				
				senha = StringUtils.str2md5(data['senha'])
				user = env['bthinker.usuario'].sudo().search([('username', '=', data['username'].lower())])
				if not user:
					erro = {'errno': 1, 'message': 'Usuário não encontrado ou senha incorreta.'}
					break
				
				if user.senha != senha:
					erro = {'errno': 1, 'message': 'Usuário não encontrado ou senha incorreta.'}
					break
				
				if user.state == "unchecked":
					erro = {'errno': 1, 'message': 'Essa conta ainda não foi ativada. Um link de ativação foi enviado para o e-mail informado durante o cadastro.'}
					break
				
				if not user.chave_id:
					erro = {'errno': 1, 'message': 'Essa conta ainda não possui uma chave associada.'}
					break

				break
			
			# Se ocorreu algum erro
			# se houve algum erro, redireciona para login
			if erro:
				if user:
					user.sudo().write({"status_ultimo_login": erro['message']})
				
				return erro
					
			
			http.request.session['user'] = {'user': user.username, 'hash': user.auto_login_hash, 'key': user.chave_id.guid}
			return {'errno': 0, 'user': user.username, 'hash': user.auto_login_hash, 'key': user.chave_id.guid}
		
		except AccessDenied:
			return {'errno': 1, 'message': 'Acesso negado.'}
		

	
	# Método que processa requisição de Login do usuário via hash unico
	def do_hash_login(self, env, data):
		
		_logger.info("HASH LOGIN DATA: %s" % data)

		try:

			fields_to_check = {
				"user": "Nome de usuário",
				"hash": "Hash"
			}

			erro = None
			while True:
				for key, value in fields_to_check.items():
					if key not in data:
						erro = {'errno': 1, 'message': '%s não está presente.' % value}
						break

					if data[key] is None:
						erro =  {'errno': 1, 'message': '%s não pode ter valor nulo.' % value}
						break

					if len(data[key].strip()) <= 0:
						erro =  {'errno': 1, 'message': '%s não pode ser vazio.' % value}
						break
				
				user = env['bthinker.usuario'].sudo().search([('username', '=', data['user'].lower()), ('auto_login_hash', '=', data['hash'])])
				if not user:
					erro =  {'errno': 1, 'message': 'Usuário não encontrado ou hash incorreta.'}
					break
				
				if user.state == "unchecked":
					erro =  {'errno': 1, 'message': 'Essa conta ainda não foi ativada. Um link de ativação foi enviado para o e-mail informado durante o cadastro.'}
					break
				
				if not user.chave_id:
					erro =  {'errno': 1, 'message': 'Não há chave definida para esse usuário.'}
					break								
				
				break

			# se houve algum erro, redireciona para login
			if erro:
				# saída padrão. Só muda no sucesso
				# html = request.env['ir.ui.view']._render_template("bthinker_qrdoor.portal_index_denied", {})
				if user:
					user.sudo().write({"status_ultimo_login": erro['message']})
					
				return erro
			

			# Para cada contrato que o usuário tem acesso:
			# Atualiza o status das porta que o usuário vai ver em sua lista
			# para saber se estão online
			try:
				
				payload = []
				for contrato in user.contrato_ids:

					for porta in contrato.porta_ids:
						payload.append(porta.guid)
										
					try:
						# tenta falar com o servidor de portas
						result = self.call_door_server(contrato.host_servidor_porta, 'getDoorStatus', payload)
						_logger.info("RESULT: %s" % result)
					except Exception as ex:
						# falhou na comunicação. Seta portas para off
						contrato.porta_ids.sudo().write({'state' : 'offline'})
						continue

					# Comunicou sem erro. Processa resposta
					if result['errno'] == 0:
						for guid, status in result['data'].items():
							porta = env['bthinker.porta'].sudo().search([('guid', '=', guid)])
							porta.sudo().write({'state' : 'online' if status == 1 else 'offline'})
					
					# Comunicou, mas houve erro. Seta pra offline
					else:						
						contrato.porta_ids.sudo().write({'state' : 'offline'})
						_logger.info("Erro 1: %s" % result['message'])
				
				env.cr.commit()
			except Exception as ex:
				env.cr.rollback()
				_logger.info("Erro2: %s" % ex)

			# Usuário está logado. Obtem as portas que o usuário tem acesso
			contratos = []
			for contrato in user.contrato_ids:
				portas = env['bthinker.porta'].sudo().search([('contrato_id', '=', contrato.id), ('usuario_ids', 'in', user.id)])
				contratos.append({'nome':contrato.partner_id.name, 'portas' : portas})
			
			values = {
				'user': user,
				'contratos': contratos,
				'periodos' : {
					'30' : 'Últimos 30 dias',
					'60' : 'Últimos 60 dias',
					'90' : 'Últimos 90 dias'
				}
			}

			_logger.info("Values: %s" % values)
			http.request.session['user'] = {'user': user.username, 'hash': user.auto_login_hash}		
			html = request.env['ir.ui.view']._render_template("bthinker_qrdoor.portal_index_authorized", values)											
			return {'errno': 0, 'message' : 'Login por hash bem sucedido.', 'html': html}
		
		except Exception as ex:
			return {'errno': 1, 'message': ex}
		
		
	
	# Salvar cadastro de novo usuário
	def check_username_profile(self, env, data):		
		valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789._-"
		
		if 'username' not in data:
			return {'errno': '1', 'message': "Nome de usuário não informado."}			
		
		if len(data['username'].strip()) <= 0:
			return {'errno': '1', 'message': "Nome de usuário não pode ser vazio."}	
		
		for c in data['username']:
			if c.lower() not in valid_chars:
				return {'errno': '1', 'message': "Nome de usuário pode conter apenas letras, números, e os caracteres '.', '-' e '_'."}	
    		
		user = env['bthinker.usuario'].sudo().search([('username', '=', data['username'])])
		if user:
			return {'errno': '1', 'message': "Nome de usuário '%s' indisponível." % data['username']}
	
		return {'errno': '0', 'message': "Nome de usuário '%s' está disponível." % data['username']}


	# Muda senha do usuário
	def change_user_password(self, env, data):		
		
		if 'username' not in data:
			return {'errno': '1', 'message': "Nome de usuário não informado."}
		
		if len(data['username'].strip()) <= 0:
			return {'errno': '1', 'message': "Nome de usuário não pode ser vazio."}					
    		
		user = env['bthinker.usuario'].sudo().search([('username', '=', data['username'])])
		
		if not user:
			return {'errno': '1', 'message': "Nome de usuário não encontrado."}
		
		user.send_password_change_email()
	
		return {'errno': '0', 'message': "Em e-mail foi enviado para %s." % StringUtils.maskEmail(user.email)}


	# Salvar cadastro de novo usuário
	def update_user_password(self, env, data):
		try:
			fields_to_check = {
				'senha': 'Senha',
				'confirma_senha': 'Confirmação de Senha',
				'hash' : 'Hash de autorização de atualização da senha'
			}

			# Verificando campos preenchidos
			for key, value in fields_to_check.items():
				if key not in data:
					return {'errno': 1, 'message': 'Parametro %s não informado.' % (value)}

				if len(data[key].strip()) <= 0:
					return {'errno': 1, 'message': 'Campo %s não pode ser vazio.' % (value)}
				
			# Identifica o usuário
			hash = data['hash']
			strJson = StringUtils.fromBase64(hash)
			user_data = StringUtils.jsonToDict(strJson)

			user = env['bthinker.usuario'].sudo().search([('username', '=', user_data['user']), ('hash_validacao', '=', user_data['hash'])])
			if not user:
				return {'errno': 1, 'message': "Sua conta não foi encontrada."}
			
			# Verificando senhas iguais
			if data['senha'] != data['confirma_senha']:
				return {'errno': 1, 'message': 'Senha e Confirmação de Senha devem ser iguais.'}
			
			
			# Atualiza a senha												
			user.sudo().write({'senha': data['senha']})

			env.cr.commit()
			return {'errno': 0, 'message': 'Dados salvos com sucesso!'}
	
		except Exception as err:
			env.cr.rollback()
			return {'errno': 500, 'message': err}	
	
	# Salvar cadastro de novo usuário
	def save_user_profile(self, env, data):
		try:
			fields_to_check = {
				'username': 'Nome de Usuário',
				'nome': 'Nome',
				'email': 'E-Mail',
				'celular': 'Celular',
				'senha': 'Senha',
				'confirma_senha': 'Confirmação de Senha',
				'hash': 'Hash de Autorização de Cadastro'
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
			
			
			convite = env['bthinker.convite_usuario'].sudo().search([('guid', '=', data['hash'])])
			if not convite:
				return {'errno': '1', 'message': "Hash de autorização de cadastro não encontrado."}	

			# Criando usuário na base
			vals = {
				'username': data['username'],
				'nome': data['nome'],
				'email': data['email'],
				'celular': data['celular'],
				'senha': data['senha'],
				'porta_ids' : [(6, 0, convite.usuario_id.porta_ids.ids)],
				'contrato_ids' :  [(4, convite.contrato_id.id)]
			}
												
			user = env["bthinker.usuario"].sudo().create(vals)
			user.action_send_enroll_mail()
			
			convite.unlink()
			env.cr.commit()
			
			return {'errno': 0, 'message': 'Dados salvos com sucesso!'}
	
		except Exception as err:
			env.cr.rollback()
			return {'errno': 500, 'message': err}
	

	# Cria uma nova visita
	
	def save_new_visit(self, env, data):
		try:
			user_data = http.request.session['user']
			
			user = env['bthinker.usuario'].sudo().search([
				('username', '=', user_data['user']), 
				('hash_validacao', '=', user_data['hash'])
			])

			if not user:
				return {'errno': 1, 'message': 'Sessão inválida. Faça login novamente.'}

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

			vals = {
				'usuario_id': user.id,
				'nome_visitante': data['nome_visitante'],
				'duracao': data['duracao'],
				'usa_uma_vez': (data['usa_uma_vez'] == "1"),
				'chave_id': chave.id,
				'executado': False,
				'finalizado': False
			}
												
			visita = env["bthinker.visita"].sudo().create(vals)					
			chave.sudo().write({'visita_id': visita.id})
			
			url = http.request.httprequest.host_url.replace("http:", "https:")
			if url.endswith('/'):
				url = url[:-1]

			url = "%s/virtualkey/visita?key=%s" % (url, chave.guid)

			_logger.info("URL VISITA: %s" % url)

			env.cr.commit()
			return {'errno': 0, 'visitor':visita.nome_visitante.upper(), 'user': visita.usuario_id.nome.upper(), 'url': url}
		
		except Exception as ex:
			env.cr.rollback()
			_logger.info(ex)
			return {'errno': 1, 'message': 'Acesso negado.'}
		
	
	def save_new_user_invite(self, env, data):
		try:
			user_data = http.request.session['user']
			
			user = env['bthinker.usuario'].sudo().search([
				('username', '=', user_data['user']), 
				('hash_validacao', '=', user_data['hash'])
			])

			if not user:
				return {'errno': 1, 'message': 'Sessão inválida. Faça login novamente.'}

			if 'contrato_convite_id' not in data:
				return {'errno': 1, 'message': 'Contrato não informado.'}			
			
			
			contrato = env['bthinker.contrato'].sudo().search([('id', '=', data['contrato_convite_id'])])
			if not contrato:
				return {'errno': 1, 'message': 'Contrato não localizado para crição do convite.'}

			# Criando usuário na base
			convite = env['bthinker.convite_usuario'].sudo().create({'usuario_id' : user.id, 'contrato_id' : contrato.id})
			
			url = http.request.httprequest.host_url.replace("http:", "https:")
			if url.endswith('/'):
				url = url[:-1]

			# Validade 24 horas, mas aqui, decontando o tz -300 na string apenas
			limit_time = convite.create_date + datetime.timedelta(hours=21)
			str_date = limit_time.strftime('%d/%m/%Y %H:%M')
			url = "%s/virtualkey/cadastro?hash=%s" % (url, convite.guid)

			_logger.info("URL CADASTRO: %s" % url)

			env.cr.commit()
			return {'errno': 0, 'url': url, 'date' : str_date}
		
		except Exception as ex:
			env.cr.rollback()
			_logger.info(ex)
			return {'errno': 1, 'message': 'Acesso negado.'}


	
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
			
			if 'method' not in data:
				return {'errno': 1, 'message': 'Método de abertura não informado.'}

			if len(data["method"].strip()) <= 0:
				return {'errno': 1, 'message': 'Método de abertur não pode ser vazio.'}
			
			model = env['bthinker.registro_acesso']
			options = dict(model._fields['metodo'].selection)
			if not data["method"] in options:
				return {'errno': 1, 'message': 'Método de abertura desconhecido: %s' % data['method']}


			# Processamento
			porta = env['bthinker.porta'].sudo().search([('guid', '=', data['door'])])
			if not porta:
				return {'errno': '1', 'message': "Porta não identificada no sistema."}
			
			chave = env['bthinker.chave'].sudo().search([('guid', '=', data['key'])])
			if not chave:
				return {'errno': '1', 'message': "Chave não identificada no sistema."}
						
			# Tudo certo com a porta?
			# Contrato ativo?
			if not porta.contrato_id:
				return {'errno': '1', 'message': "Não há um contrato associado a esta porta."}
			
			if not porta.contrato_id.state == 'active':
				return {'errno': '1', 'message': "Porta vinculada a um contrato inativo."}


			# Verificando a permissão do usuário na porta
			# Seje o usuário requisitando ou um de seus visitantes
			usuario = None
			if chave.visita_id:
				
				if chave.visita_id.usuario_id:
					usuario = chave.visita_id.usuario_id
				
				if chave.visita_id.finalizado:
					return {'errno': '1', 'message': "Visita já finalizada"}
				
				if chave.visita_id.usa_uma_vez and chave.visita_id.executado:
					return {'errno': '1', 'message': "Chave de visita já utilizada."}

				current_time = datetime.datetime.now()
				limit_time = chave.visita_id.create_date + datetime.timedelta(hours=chave.visita_id.duracao)

				if current_time > limit_time:
					chave.visita_id.write({'finalizado':True})
					return {'errno': '1', 'message': "Horário para visita já encerrado."}

			elif chave.usuario_id:
				usuario = chave.usuario_id


			#Identificação do usuário
			if not usuario:
				return {'errno': '1', 'message': "Usuário não identificado para a chave informada"}

			# o que une porta e usuário é o contrato
			# então, verificamos se existe relação entre o usuário e a porta
			contrato = env['bthinker.contrato'].sudo().search([('porta_ids', 'in', porta.id), ('usuario_ids', 'in', usuario.id)])
			if not contrato:
				return {'errno': '1', 'message': "Não foi encontrada relação para o par Chave/Porta."}
			

			# Gravação de Logs de Acesso e tratativas finais
			# se é chave de visita
			if chave.visita_id:				
				chave.visita_id.write({'executado':True, 'finalizado': chave.visita_id.usa_uma_vez})
				
			
			# Atualiza data de ultima utilização da chave
			chave.sudo().write({'ultimo_uso' : datetime.datetime.now() })

			# Aciona a porta
			payload = {
				'door': porta.guid
			}				
			result = self.call_door_server(contrato.host_servidor_porta,'openDoor', payload)
			_logger.info("ESP DATA: %s" % result)

			# grava o acesso
			nome_pessoa = usuario.nome
			tipo = 'user'
			if chave.visita_id:
				nome_pessoa = '%s (VISITANTE)' % chave.visita_id.nome_visitante
				tipo = 'visitor'

			env["bthinker.registro_acesso"].sudo().create({
				'contrato_id': porta.contrato_id.id,
				'nome_pessoa': nome_pessoa,
				'usuario_id': usuario.id,
				'porta_id': porta.id,
				'tipo': tipo,
				'metodo': data['method'],
				'resultado': 'sucesso' if result['errno'] == 0 else 'falha'
			})

			return {'errno': result['errno'], 'message': result['message']}	

		except Exception as ex:
			return {'errno': 1, 'message': ex}	
	


	def search_report_records(self, env, data):
		
		_logger.info("search_report_records: %s" % data)
		try:
			
			# Validando campos obrigatórios
			if 'contrato_relatorio' not in data:
				return {'errno': 1, 'message': 'Contato não informado.'}
			
			if 'periodo_relatorio' not in data:
				return {'errno': 1, 'message': 'Período não informado.'}
			
			if 'page' not in data:
				return {'errno': 1, 'message': 'Página não informada.'}
						

			now = datetime.datetime.now()
			date_limit = now - datetime.timedelta(days=int(data['periodo_relatorio']))
			filter = [
				('contrato_id', '=', int(data['contrato_relatorio'])),
				('create_date', '>=', date_limit)				
			]

			# se informou nome, adiciona condição no filtro
			if 'nome_relatorio' in data:
				if len(data["nome_relatorio"].strip()) > 0:
					filter.append(('nome_pessoa', 'ilike', data['nome_relatorio'].strip()))
			

			offset = int(data['page']) * 25
			limit = 25
			
			_logger.info("offset %d, limit %d" % (offset, limit))


			records = env["bthinker.registro_acesso"].sudo().search(filter, order='create_date DESC', offset=offset, limit=limit)
			data = []
			for rec in records:
				date = rec.create_date - datetime.timedelta(hours=3)
				fdate = date.strftime('%d/%m/%Y')
				ftime = date.strftime('%H:%M:%S')
				data.append({
					'nome': rec.nome_pessoa,
					'porta': rec.porta_id.nome,
					'tipo': ModelUtils.get_selection_label(rec, 'tipo', rec.tipo),
					'metodo': ModelUtils.get_selection_label(rec, 'metodo', rec.metodo),
					'resultado': ModelUtils.get_selection_label(rec, 'resultado', rec.resultado),
					'data': fdate,
					'hora': ftime
				})
			return {'errno': 0, 'data': data, 'count':len(data)}
		except Exception as ex:
			return {'errno': 1, 'message': ex}	
		


	def call_door_server(self, server_host, endpoint, payload):
		
		url = 'http://%s:8200/qrdoor/%s' % (server_host, endpoint)
		headers = {
			'Content-Type': 'application/json',
		}		
		
		response = requests.post(url, json=payload, headers=headers)
		response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
		response_data = response.json()  # Processa a resposta JSON
		return response_data
			