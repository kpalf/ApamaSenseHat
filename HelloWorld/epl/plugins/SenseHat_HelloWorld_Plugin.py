'''
	A simple HelloWorld type of plugin to test scrolling a message on the SenseHAT on a Raspberry Pi

	Copyright (c) 2018 Kevin Palfreyman

'''

from sense_hat import SenseHat
from apama.eplplugin import EPLAction, EPLPluginBase

class SenseHatHelloWorldClass(EPLPluginBase):

	def __init__(self,init):
		super(SenseHatHelloWorldClass,self).__init__(init)
		self.getLogger().info("SenseHatHelloWorldClass initialised with config: %s" % self.getConfig())
		
	@EPLAction("action<string>")
	def show_message(self, message):
		"""
		This method will scroll the message passed to it.

		@param message:	The test to be shown on the SenseHat.
		"""
		sense = SenseHat()
		sense.show_message(message)





