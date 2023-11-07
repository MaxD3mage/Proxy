from aiohttp import web, ClientConnectorError, ClientResponseError, ClientSession


async def handle(request):
    try:
        async with ClientSession() as session:
            async with session.get(request.url) as resp:
                content = await resp.content.read()
                return web.Response(body=content, content_type=resp.content_type)
    except (BaseException, ClientConnectorError, ClientResponseError, UnicodeDecodeError) as e:
        return web.Response(text=str(e), status=500)


app = web.Application()
app.router.add_route('*', '/{path:.*}', handle)

web.run_app(app, host='127.0.0.1', port=8080)
