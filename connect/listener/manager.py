from .listener import ConnectListener


class ListenerManager:
    def __init__(self):
        self.listeners = {}

    async def create_listener(self, ip, port, socks_manager, sio_team_server):
        """
        Create a new ConnectListener and add it to the manager.

        Args:
            ip (str): The IP address or hostname of the server.
            port (int): The port number to connect to on the server.
            socks_manager: Manager to create and shutdown socks servers.
            sio_team_server:
        """
        # Check to see if a listener already exists.
        if (ip, port) in self.listeners:
            await sio_team_server.emit('error', f'A listener for {ip}:{port} already exists.')
            return

        # Create and Start the listener
        new_listener = ConnectListener(ip, port, socks_manager, sio_team_server)
        await new_listener.start()

        # Store the listener in the dictionary
        self.listeners[(ip, port)] = new_listener

        await sio_team_server.emit('success', f'Listener started on {ip}:{port}')

    async def stop_listener(self, ip, port, sio_team_server):
        # Check if an application exists for the given IP and port
        if (ip, port) not in self.listeners:
            await sio_team_server.emit('error', f'No listener found for {ip}:{port}')

        await sio_team_server.emit('information', f'Attempting to stop listener {ip}:{port}. This may take awhile.')

        # Stop the server and cleanup
        listener = self.listeners[(ip, port)]
        await listener.stop()

        # Remove the application from the dictionary
        del self.listeners[(ip, port)]

        await sio_team_server.emit('success', f'Listener stopped on {ip}:{port}')

    def get_listeners(self):
        """
        Get information about all managed listeners.

        Returns:
            list: A list of dictionaries containing information about each listener.
        """
        listener_info = []
        for listener in self.listeners.keys():
            info = {
                'ip': listener[0],
                'port': listener[1],
            }
            listener_info.append(info)
        return listener_info
