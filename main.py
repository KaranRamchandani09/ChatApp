import os
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
# to use buttons:
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from socketIO_client import SocketIO
#import socket_client
import sys

from kivy.uix.scrollview import ScrollView

kivy.require("1.10.1")

class scrollablelabel(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.layout=GridLayout(cols=1,size_hint_y=None)
		self.add_widget(self.layout)
		self.chat_history = Label(size_hint_y=None, markup=True)
		self.scroll_to_point=Label()
		self.layout.add_widget(self.chat_history)
		self.layout.add_widget(self.scroll_to_point)

	def update_chat_history(self,message):
		self.chat_history.text+='\n'+message
		self.layout.height=self.chat_history.texture_size[1]+15
		self.chat_history.height=self.chat_history.texture_size[1]
		self.chat_history.text_size=(self.chat_history.width*0.98,None)
		self.scroll_to(self.scroll_to_point)

		

	def update_chat_history_layout(self, _=None):

	 	# Set layout height to whatever height of chat history text is + 15 pixels
		# (adds a bit of space at the bottom)
		# Set chat history label to whatever height of chat history text is
		# Set width of chat history text to 98 of the label width (adds small margins)
		self.layout.height = self.chat_history.texture_size[1] + 15
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width * 0.98, None)

	 	
		
		


class InfoPage(GridLayout):
	# runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.cols=1
		self.message=Label(halign="center" , valign="middle")
		self.message.bind(width=self.update_text_width)
		self.add_widget(self.message)


	
		
	def update_info(self,message):
		self.message.text=message
		
	def update_text_width(self,*_):
		self.message.text_size=(self.message.width*0.9,None)

class ChatPage(GridLayout):

	 # runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.rows =2
		self.cols = 1 # used for our grid
		self.history=scrollablelabel(height=Window.size[1]*0.9,size_hint_y=None)
		self.add_widget(self.history)
		self.new_message=TextInput(width=Window.size[0]*0.8,size_hint_x=None,multiline=False)
		self.send1=Button(text="send")
		self.send1.bind(on_press=self.send_message)
		
		bottom_line1=GridLayout(cols=2)
		bottom_line1.add_widget(self.new_message)
		bottom_line1.add_widget(self.send1)
		self.add_widget(bottom_line1)

		
		Window.bind(on_key_down=self.on_key_down)
		Clock.schedule_once(self.focus_text_input,1)
		socket_client.start_listening(self.incoming_message,show_error)
		self.bind(size=self.adjust_fields)

	def incoming_message(self, username, message):
		self.history.update_chat_history({message})

       

	 # Updates page layout
	def adjust_fields(self, *_):

		# Chat history height - 90%, but at least 50px for bottom new message/send button part
		if Window.size[1] * 0.1 < 50:
			new_height = Window.size[1] - 50
		else:
			new_height = Window.size[1] * 0.9
		self.history.height = new_height

		# New message input width - 80%, but at least 160px for send button
		if Window.size[0] * 0.2 < 160:
			new_width = Window.size[0] - 160
		else:
			new_width = Window.size[0] * 0.8
		self.new_message.width = new_width

		# Update chat history layout
		# self.history.update_chat_history_layout()
		Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

	def on_key_down(self,instance,keyboard,keycode,text,modifiers):
		if(keycode==40):
			self.send_message(None)
		  



	def focus_text_input(self, _):
    	 self.new_message.focus = True

	def update_chat_history_layout(self, _=None):
		self.layout.height = self.chat_history.texture_size[1] + 15
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width * 0.98, None)

     	
  
	def send_message(self,_):
		message=self.new_message.text
		self.new_message.text=""
		if message:
			  #self.history.update_chat_history(f'[color=dd2020]{chatApp.connectpage.username.text}[/color] > {message}')
			  socket_client.send(message)

		# As mentioned above, we have to shedule for refocusing to input field
		Clock.schedule_once(self.focus_text_input, 0.1)

		
class ConnectPage(GridLayout):
	# runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 2  # used for our grid

		# Read settings from text file, or use empty strings
		if os.path.isfile("prev_details.txt"):
			with open("prev_details.txt","r") as f:
				d = f.read().split(",")
				prev_ip = d[0]
				prev_port = d[1]
				prev_username = d[2]
		else:
			prev_ip = ''
			prev_port = ''
			prev_username = ''

		self.add_widget(Label(text='IP:'))  # widget #1, top left
		self.ip = TextInput(text=prev_ip, multiline=False)  # defining self.ip...
		self.add_widget(self.ip) # widget #2, top right

		self.add_widget(Label(text='Port:'))
		self.port = TextInput(text=prev_port, multiline=False)
		self.add_widget(self.port)

		self.add_widget(Label(text='Username:'))
		self.username = TextInput(text=prev_username, multiline=False)
		self.add_widget(self.username)

		
		self.join = Button(text="Join")
		self.join.bind(on_press=self.join_button)
		self.add_widget(Label())  # just take up the spot.
		self.add_widget(self.join)
		
		

	def join_button(self, instance):
		port = self.port.text
		ip = self.ip.text
		username = self.username.text
		with open("prev_details.txt","w") as f:
			#f.write(f"{ip},{port},{username}")
		#print(f"Joining {ip}:{port} as {username}")
		# Create info string, update InfoPage with a message and show it
		info = "Joining {ip}:{port} as {username}"
		chatApp.infopage.update_info(info)
		chatApp.screen_manager.current = 'Info'
		Clock.schedule_once(self.connect, 1)
		

	def connect(self, _):

		# Get information for sockets client
		port = int(self.port.text)
		ip = self.ip.text
		username = self.username.text
		# socketIO = SocketIO(ip, port)
		# socketIO.wait(seconds=1)

		if not socket_client.connect(ip, port, username, show_error):
			return

	    


		  

		# Create chat page and activate it
		chatApp.create_chat_page()
		chatApp.screen_manager.current = 'Chat'
	
		
	
def show_error(message):

	chatApp.infopage.update_info(message)
	chatApp.screen_manager.current = 'Info'
	Clock.schedule_once(sys.exit, 10)            
	


class EpicApp(App):                         
	def build(self):
		self.screen_manager=ScreenManager()
		self.connectpage=ConnectPage()
		screen=Screen(name="connect")
		screen.add_widget(self.connectpage)
		self.screen_manager.add_widget(screen)
		
		self.infopage=InfoPage()
		screen=Screen(name="Info")
		screen.add_widget(self.infopage)
		self.screen_manager.add_widget(screen)
		
		return self.screen_manager
		
	def create_chat_page(self):
		self.chat_page = ChatPage()
		screen = Screen(name='Chat')
		screen.add_widget(self.chat_page)
		self.screen_manager.add_widget(screen)
		return self.screen_manager
 


if __name__ == "__main__":
	chatApp=EpicApp()
	chatApp.run()
	