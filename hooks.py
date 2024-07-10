from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__) 

def pre_init_hook(cr):
	return

def post_init_hook(cr, registry):	
	
	#env = api.Environment(cr, SUPERUSER_ID, {})
	_logger.info("Iniciando rotinas POST_INIT_HOOK")

	#_logger.info("Criando indices de tabelas em banco de dados")
	#cr.execute('DROP INDEX IF EXISTS zkmango_pushcommand_sn_seq_priority_result_index')
	#cr.execute('CREATE INDEX zkmango_pushcommand_sn_seq_priority_result_index ON zkmango_pushcommand (serial, sequence, priority desc, result NULLS FIRST)')

	# Other odoo modules check for the index existence before calling the create index command.
	# Personal question: Since we call "DROP INDEX IF EXISTS" right before index creation, do we really need to check??	
	# cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('zkmango_pushcommand_sn_seq_priority_result_index'))
	# if not cr.fetchone():
	
	return
	
def uninstall_hook(cr, registry):

	# We dont delete the indexes created on the post_init hook because they are deletes
	# along with the tables, when odoo is deleting the module tables.
	# So, no need to delete indexes.
	# Other unistall processes can be done here.
	return


def post_load():
	return