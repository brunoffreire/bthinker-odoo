# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


# Classe de configuração do módulo de acesso
class module_settings(models.TransientModel):
	_inherit = "res.config.settings"
	
	door_server_url = fields.Char(string="URL")
	door_server_callback_url = fields.Char(string="URL de Callback")
	

	@api.model
	def get_values(self):
		res = super(module_settings, self).get_values()
		res['door_server_url'] = self.env['ir.config_parameter'].sudo().get_param('bthinker_qrdoor.door_server_url')
		if not res['door_server_url']:
			res['door_server_url'] = "http://localhost:8200/qrdoor"
		
		res['door_server_callback_url'] = self.env['ir.config_parameter'].sudo().get_param('bthinker_qrdoor.mango_callback_url')
		if not res['door_server_callback_url']:
			res['door_server_callback_url'] = "%s/%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "qrdoor")

		return res

	@api.model
	def set_values(self):
		self.env['ir.config_parameter'].sudo().set_param('bthinker_qrdoor.door_server_url', self.door_server_url)
		self.env['ir.config_parameter'].sudo().set_param('bthinker_qrdoor.door_server_callback_url', self.door_server_callback_url)

		super(module_settings, self).set_values()

