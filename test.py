import unittest
import asyncio
from datetime import timedelta
from unittest import mock

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp_client_cache.backends.sqlite import SQLiteBackend

from Server import handle


class TestHandleRequest(AioHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()

    async def get_application(self):
        app = web.Application()
        app.router.add_route('*', '/{path:.*}', handle)
        return app

    @unittest_run_loop
    async def test_handle_request(self):
        request_headers = {'Proxy-Authorization': 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='}
        response_text = 'Proxy Authentication Required'

        with mock.patch('Server.CachedSession') as mock_session:
            mock_cache = SQLiteBackend(expire_after=timedelta(days=30))
            mock_session.return_value.__aenter__.return_value.get.return_value.text.return_value = response_text

            resp = await self.client.get('/', headers=request_headers)
            response_data = await resp.text()

            self.assertEqual(resp.status, 407)
            self.assertEqual(response_data, response_text)

    @unittest_run_loop
    async def test_handle_request_no_authentication(self):
        resp = await self.client.get('/')
        self.assertEqual(resp.status, 407)
        self.assertTrue('Proxy-Authenticate' in resp.headers)
        self.assertEqual(await resp.text(), 'Proxy Authentication Required')

    @unittest_run_loop
    async def test_handle_request_incorrect_authentication(self):
        request_headers = {'Proxy-Authorization': 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='}

        resp = await self.client.get('/', headers=request_headers)
        self.assertEqual(resp.status, 407)
        self.assertTrue('Proxy-Authenticate' in resp.headers)
        self.assertEqual(await resp.text(), 'Proxy Authentication Required')

    @unittest_run_loop
    async def test_handle_request_correct_authentication(self):
        request_headers = {'Proxy-Authorization': 'Basic YWRtaW5fbG9naW46YWRtaW5fcGFzc3dvcmQ='}

        resp = await self.client.get('/', headers=request_headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(await resp.text(), 'Proxy Authentication Required')


if __name__ == '__main__':
    unittest.main()
