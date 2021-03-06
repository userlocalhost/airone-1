import json

from airone.lib.test import AironeViewTest
from entity.models import Entity

from unittest import mock
from webhook.models import Webhook


class APITest(AironeViewTest):
    @mock.patch('webhook.api_v1.views.requests')
    def test_create_invalid_endpoint_webhook(self, mock_requests):
        user = self.guest_login()
        entity = Entity.objects.create(name='test-entity', created_user=user)

        # Declare requests mock that responds HTTP 400(ERROR)
        mock_resp = mock.Mock()
        mock_resp.ok = False
        mock_resp.text = 'test-failure'
        mock_requests.post.return_value = mock_resp

        resp = self.client.post('/webhook/api/v1/%s' % entity.id, json.dumps({
            'webhook_url': 'https://example.com',
            'label': 'test endpoint',
            'request_headers': [{'key': 'content-type', 'value': 'application/json'}],
            'is_enabled': True,
        }), 'application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['msg'], 'Succeded in registering Webhook URL')

        webhook = Webhook.objects.get(id=resp.json()['webhook_id'])
        self.assertEqual(webhook.url, 'https://example.com')
        self.assertEqual(webhook.label, 'test endpoint')
        self.assertEqual(webhook.headers, json.dumps({'content-type': 'application/json'}))
        self.assertTrue(webhook.is_enabled)
        self.assertFalse(webhook.is_verified)

    @mock.patch('webhook.api_v1.views.requests')
    def test_create_valid_endpoint_webhook(self, mock_requests):
        user = self.guest_login()
        entity = Entity.objects.create(name='test-entity', created_user=user)

        # Declare requests mock that responds HTTP 200(Success)
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.text = 'test-failure'
        mock_requests.post.return_value = mock_resp

        resp = self.client.post('/webhook/api/v1/%s' % entity.id, json.dumps({
            'webhook_url': 'https://example.com',
            'label': 'test endpoint',
            'request_headers': [{'key': 'content-type', 'value': 'application/json'}],
            'is_enabled': True,
        }), 'application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['msg'], 'Succeded in registering Webhook URL')

        webhook = Webhook.objects.get(id=resp.json()['webhook_id'])
        self.assertEqual(webhook.url, 'https://example.com')
        self.assertEqual(webhook.label, 'test endpoint')
        self.assertEqual(webhook.headers, json.dumps({'content-type': 'application/json'}))
        self.assertTrue(webhook.is_enabled)
        self.assertTrue(webhook.is_verified)

    @mock.patch('webhook.api_v1.views.requests')
    def test_edit_invalid_webhook(self, mock_requests):
        user = self.guest_login()
        entity = Entity.objects.create(name='test-entity', created_user=user)

        # Declare requests mock that responds HTTP 200(Success)
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.text = 'test-failure'
        mock_requests.post.return_value = mock_resp

        resp = self.client.post('/webhook/api/v1/%s' % entity.id, json.dumps({
            'id': 999999,  # invlaid webhook id
            'webhook_url': 'https://example.com',
            'label': 'test endpoint',
            'request_headers': [{'key': 'content-type', 'value': 'application/json'}],
            'is_enabled': True,
        }), 'application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content.decode('utf-8'), 'Invalid Webhook ID is specified')

    @mock.patch('webhook.api_v1.views.requests')
    def test_edit_webhook_instance(self, mock_requests):
        user = self.guest_login()
        entity = Entity.objects.create(name='test-entity', created_user=user)
        webhook = Webhook.objects.create(**{
            'url': 'https://example.com',
            'label': 'initial-label',
        })

        # Declare requests mock that responds HTTP 200(Success)
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.text = 'test-failure'
        mock_requests.post.return_value = mock_resp

        resp = self.client.post('/webhook/api/v1/%s' % entity.id, json.dumps({
            'id': webhook.id,
            'webhook_url': 'https://changed-example.com',
            'label': 'changed-label',
            'request_headers': [{'key': 'content-type', 'value': 'application/json'}],
            'is_enabled': True,
        }), 'application/json')
        self.assertEqual(resp.status_code, 200)

        webhook.refresh_from_db()
        self.assertEqual(webhook.id, resp.json()['webhook_id'])
        self.assertEqual(webhook.url, 'https://changed-example.com')
        self.assertEqual(webhook.label, 'changed-label')
        self.assertEqual(webhook.headers, json.dumps({'content-type': 'application/json'}))
        self.assertTrue(webhook.is_enabled)
        self.assertTrue(webhook.is_verified)
