import asyncio
from aiohttp import ClientSession, web, client_exceptions


class Proxy:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.site_url = None
        self.html_content = """
    <html>
    <head>
        <title>Пизда ERROR</title>
    </head>
    <body>
        <h1>Всё пошло по жопе</h1>
        <p>Екстренная катапультация.</p>
    </body>
    </html>
    """

    async def init_server(self):
        app = web.Application()
        #app.router.add_route('*', '/http://{path:.*}', self.handle)
        #app.router.add_route('*', '/https://{path:.*}', self.handle)
        app.router.add_route('*', '/{path:.*}', self.handle)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        while True:
            await asyncio.sleep(3600)

    async def handle(self, request):
        url = str(request.rel_url)[1:]
        if self.site_url is None and url.startswith('http://') or url.startswith('https://'):
            self.site_url = url
        if not (url.startswith('http://') or url.startswith('https://')):
            url = self.site_url + url
        print(url)
        response = await self.get_site(url)
        if response is None:
            return
        if response.status == 200:
            #raise web.HTTPFound(location=url)
            return web.Response(body=self.html_content, content_type='text/html')

    async def get_site(self, url):
        try:
            async with ClientSession() as session:
                async with session.get(url=url) as response:
                    if response.status == 200:
                        try:
                            self.html_content = await response.text()
                        except UnicodeDecodeError:
                            return None
                    return response
        except client_exceptions.InvalidURL:
            return None


def main():
    proxy = Proxy('localhost', 8080)
    asyncio.run(proxy.init_server())


if __name__ == '__main__':
    main()