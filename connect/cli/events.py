import json
import socketio


class Events:
    sio = socketio.Client()

    def __init__(self, notify, set_cli_properties):
        self.notify = notify
        self.set_cli_properties = set_cli_properties
        self.sio.on('agents', self.agents)
        self.sio.on('implants', self.implants)
        self.sio.on('listeners', self.listeners)
        self.sio.on('default', self.default)
        self.sio.on('error', self.error)
        self.sio.on('information', self.information)
        self.sio.on('success', self.success)

    def agents(self, data):
        self.set_cli_properties(agents=data)
        table = self.create_table('AGENTS', data[0].keys(), data)
        self.notify(table, 'DEFAULT')

    def implants(self, data):
        self.set_cli_properties(implants=data)
        table = self.create_table('IMPLANTS', data[0].keys(), data)
        self.notify(table, 'DEFAULT')

    def listeners(self, data):
        table = self.create_table('LISTENERS', data[0].keys(), data)
        self.notify(table, 'DEFAULT')

    def default(self, data):
        self.notify(data, 'DEFAULT')

    def error(self, data):
        self.notify(data, 'ERROR')

    def information(self, data):
        self.notify(data, 'INFORMATION')

    def success(self, data):
        self.notify(data, 'SUCCESS')
    # Calculate the length of the longest value in a list of dictionaries
    @staticmethod
    def longest_value(items: list[dict]):
        return max(len(value) for item in items for value in item.values())

    # Generate a formatted table output
    @staticmethod
    def create_table(title, columns: list, items: list[dict]) -> str:
        # Calculate the maximum width for each column
        col_widths = [len(col) for col in columns]
        for item in items:
            for idx, col in enumerate(columns):
                col_widths[idx] = max(col_widths[idx], len(str(item.get(col, ''))) + 4)

        # Create the table header
        header = f"{title:^{sum(col_widths) + len(columns) - 1}}\n"
        header += ' '.join([f"{col:^{width}}" for col, width in zip(columns, col_widths)]) + '\n'
        header += ' '.join(['-' * width for width in col_widths]) + '\n'

        # Create the table rows
        rows = []
        for item in items:
            row = ' '.join([f"{str(item.get(col, '')):^{width}}" for col, width in zip(columns, col_widths)]) + '\n'
            rows.append(row)

        # Combine header and rows to form the table
        table = header + ''.join(rows)
        return table
