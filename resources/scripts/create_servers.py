import asyncio
from aiohttp import web
import random

class ListenerManager:
    def __init__(self):
        self.applications = {}  # Dictionary to store AioHTTP applications

    async def create_application(self, ip, port):
        # Check if an application already exists for the given IP and port
        if (ip, port) in self.applications:
            raise ValueError(f"An application for {ip}:{port} already exists")

        # Create a new AioHTTP web application
        app = web.Application()

        # Define routes and handlers for the application
        app.router.add_get('/', self.handle_request)

        # Create a server to listen on the specified IP and port
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, ip, port)

        # Start the server
        await site.start()

        # Store the application and site in the dictionary
        self.applications[(ip, port)] = {
            'app': app,
            'runner': runner,
            'site': site
        }

        print(f"Application started on {ip}:{port}")

    async def handle_request(self, request):
        return web.Response(text="Hello, World!")

    async def stop_application(self, ip, port):
        # Check if an application exists for the given IP and port
        if (ip, port) not in self.applications:
            raise ValueError(f"No application found for {ip}:{port}")

        # Stop the server and cleanup
        app_info = self.applications[(ip, port)]
        await app_info['site'].stop()
        await app_info['runner'].cleanup()

        # Remove the application from the dictionary
        del self.applications[(ip, port)]

        print(f"Application stopped on {ip}:{port}")

    async def stop_all_applications(self):
        # Stop all running applications
        for (ip, port) in list(self.applications.keys()):
            await self.stop_application(ip, port)


if __name__ == '__main__':
    listener_manager = ListenerManager()

    while True:
        user_input = input('create server> ')
        try:
            if user_input:
                asyncio.run(listener_manager.stop_application(user_input.split()[0], int(user_input.split()[1])))
                continue

            # Create and start a new AioHTTP application
            asyncio.run(listener_manager.create_application('127.0.0.1', random.randint(1500,3000)))
            print(listener_manager.applications)
            # Create and manage an event loop explicitly
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
        except KeyboardInterrupt:
            pass
        finally:
            pass
            # Stop all applications when the program exits
            #asyncio.run(listener_manager.stop_all_applications())
