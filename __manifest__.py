# -*- coding: utf-8 -*-
# Autor: B-Thinker
{
	'name': "Módulo Odoo QRDoor da B-Thinker",

	'summary': """
		Módulo de gestão da solução de acesso QRDoor
	""",

	'description': """
		Módulo de gestão da solução de acesso QRDoor 
        e chaves virtuais.
	""",

	'author': "B-Thinker",
	'website': "http://www.b-thinker.com.br",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'Básico',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'mail', 'contacts', 'snailmail'],

	#Pillow not included
	'external_dependencies' : {'python': ['pycryptodome', 'fpdf', 'qrcode', 'psycogreen', 'uuid']},

	# always loaded
	'data': [		
		#'data/assets.xml',		
		#'data/model_timeinterval.xml',
		#'data/initial_data.xml',		
		'views/admin_chave.xml',
        'views/admin_contrato.xml',
        'views/admin_porta.xml',
        'views/admin_usuario.xml',
        'views/admin_visita.xml',
        'views/admin_menu.xml',
        'views/admin_registro_acesso.xml',
        'views/admin_settings.xml',        
		'views/portal_layout.xml',
        'views/portal_index.xml',
        'views/portal_index_authorized.xml',
        'views/portal_index_denied.xml',        
        'views/portal_login.xml',
        'views/portal_cadastro.xml',
        'views/portal_muda_senha.xml',
        'views/portal_visita.xml',
        'views/portal_validate.xml',
        
		#'views/report_visit_ticket.xml',
		#'views/portal_layout.xml',

		'security/security.xml',
		'security/ir.model.access.csv',
	],

	# Aparentemente, para que sintaxe QWEB funcione nos widgets,
	# como estruturas if ou loops, é necessário registrar os arquivos que 
	# usarão a engine qweb. Por isso a linha abaixo.
	# TO-DO: Verificar se isso é fato ou se a linha abixo pode ser removida
	# do manifesto, sem quebrar o funcionamento do sistema.
	'qweb': [
		'static/src/xml/*.xml'
	],
	
	# only loaded in demonstration mode
	#'demo': [
	#	'demo/demo.xml',
	#],

	#'assets': {        
    #    'web.assets_backend': [
	#		'bthinker/static/src/js/BTManager.js',
	#		'bthinker/static/src/css/BTManager.css',
	#		'bthinker/static/src/xml/BTManager.xml'
    #    ]
    #},

	'installable': True,
	'application': True,
	'auto_install': False,
	'pre_init_hook': 'pre_init_hook',
	'post_init_hook': 'post_init_hook',
	'uninstall_hook': 'uninstall_hook',
	'post_load': 'post_load'
}