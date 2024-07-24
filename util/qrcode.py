from io import BytesIO
from PIL import Image
from odoo import modules, tools

import qrcode
import base64
import logging
_logger = logging.getLogger(__name__) 

class QRCode:

	def get_image(self, text, include_logo=False, logo_image=None):
		_logger.info("")		
		_logger.info("QRCODE GETIMAGE")		
		QRcode = qrcode.QRCode(
			error_correction=qrcode.constants.ERROR_CORRECT_H,
			border=2
		)
		
		QRcode.add_data(text)
		QRcode.make()
		QRcolor = 'Black'
		QRimg = QRcode.make_image(
			fill_color=QRcolor, back_color="white").convert('RGB')

		if include_logo:
			if not logo_image:
				image_path = modules.module.get_resource_path('bthinker','static/img','logo-qrcode.png')
				logo_image = Image.open(image_path)

		if logo_image:
			pos = ((QRimg.size[0] - logo_image.size[0]) // 2, (QRimg.size[1] - logo_image.size[1]) // 2)			
			QRimg.paste(logo_image, pos)
		
		_logger.info('QR code generated!')

		return QRimg			

	def get_base64(self, text, include_logo=False, logo_image=None):
		_logger.info("")		
		_logger.info("QRCODE GETBASE64")		
		img = self.get_image(text, include_logo, logo_image)
		buffered = BytesIO()
		img.save(buffered, format="PNG")
		return base64.b64encode(buffered.getvalue()).decode("utf-8")
