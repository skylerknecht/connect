import time

from connect import cli, color, util

class Connection():

    system_information = {}
    menu_options = {}
    status = 'Pending'

    def __init__(self, implant_format, connection_id):
        self.connection_id = connection_id
        self.implant_format = implant_format
        self.implant_requested = self.get_current_time()
        self.last_checkin = self.get_current_time()
        self.setup_menu()

    def __str__(self):
        return f'Implant Requested {self.implant_requested} || Last Checkin: {self.last_checkin} || Status: {self.status} || Implant Format: {self.implant_format}'

    def display_username(self):
        color.normal(self.system_information['username'])
        return 0
        
    def setup_menu(self):
        self.menu_options['display username'] = (self.display_username, 'Displays the username.')

    def update_checkin(self):
        self.status = 'Connected'
        self.last_checkin = self.get_current_time()
        return 0

    def interact(self):
        connection_cli = cli.CommandLine(f'connect ({self.connection_id}) ~#', connection=self)
        connection_cli.run()
        return 0

    @staticmethod
    def get_current_time():
        return time.strftime("%H:%M:%S", time.localtime())
