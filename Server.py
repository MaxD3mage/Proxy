from aiohttp import web, ClientConnectorError, ClientResponseError, ClientSession, BasicAuth
import logging
from aiohttp_client_cache import CachedSession, SQLiteBackend
from datetime import timedelta
import ssl


logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

cache = SQLiteBackend(expire_after=timedelta(days=30))


async def handle(request):
    try:
        logging.info("Get authentication")

        auth_header = request.headers.get('Proxy-Authorization')
        if not auth_header:
            return web.Response(status=407, headers={'Proxy-Authenticate': 'Basic realm="Proxy Authentication"'},
                                text='Proxy Authentication Required')

        auth = BasicAuth.decode(auth_header)
        if auth.login != 'admin_login' or auth.password != 'admin_password':
            logging.info("login or password incorrect")
            return web.Response(status=407, headers={'Proxy-Authenticate': 'Basic realm="Proxy Authentication"'},
                                text='Proxy Authentication Required')

        logging.info(f'Handling request for {request.url}')
        async with CachedSession(cache=cache) as session:
            async with session.get(request.url, ssl=ssl.create_default_context()) as resp:

                logging.info(f'Response received for {request.url}')

                response = web.StreamResponse()
                response.content_type = resp.content_type
                response.charset = resp.charset

                await response.prepare(request)

                async for data in resp.content.iter_any():
                    await response.write(data)

                return response
    except (BaseException, ClientConnectorError, ClientResponseError, UnicodeDecodeError, ConnectionResetError) as e:
        logging.error(f'Error occurred while handling request for {request.url}: {str(e)}')

        return web.Response(text=str(e), status=500)


app = web.Application()
app.router.add_route('*', '/{path:.*}', handle)

web.run_app(app, host='127.0.0.1', port=8080)
