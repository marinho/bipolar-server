import responses
import json
from datetime import datetime
from django.test import TestCase
from django.test.client import Client
from django.core.exceptions import ValidationError
from tastypie.test import ResourceTestCase

from models import Account, Feature, Qualifier
from webhooks import PusherWebhook, UrlWebhook


class TestAccount(TestCase):
    def tearDown(self):
        Account.objects.all().delete()

    def test_basic(self):
        account = Account.objects.create(
            name="T Dispatch",
            )
        self.assertEqual(account.shortcode[:4], "TTSP")
        self.assertEqual(len(account.shortcode), 8)
        self.assertEqual(len(account.api_key), 32)
        self.assertTrue(isinstance(account.creation, datetime))


class TestFeature(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name="T Dispatch",
            )

    def tearDown(self):
        Account.objects.all().delete()

    def test_basic_validation(self):
        feature = Feature(
            account=self.account,
            name="Crm.Business",
            )
        try:
            feature.full_clean()
        except ValidationError as e:
            self.assertEqual(e.message_dict, {'__all__': [u'Name must start with a letter and contain only letters, numbers and underscore.']})

    def test_basic(self):
        feature = Feature.objects.create(
            account=self.account,
            name="crm_business",
            )
        self.assertEqual(feature.name, "crm_business")


class TestQualifier(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name="T Dispatch",
            )
        self.feature1 = self.account.features.create(
            name="crm_business",
            permission_type=Feature.TYPE_BOOLEAN,
            )
        self.feature2 = self.account.features.create(
            name="crm_person",
            permission_type=Feature.TYPE_BOOLEAN,
            )
        self.feature3 = self.account.features.create(
            name="crm_locations_limit",
            permission_type=Feature.TYPE_LIMIT,
            )

    def tearDown(self):
        Account.objects.all().delete()

    def test_basic(self):
        qualifier = Qualifier.objects.create(
            account=self.account,
            name="master",
            )
        self.assertEqual(qualifier.name, "master")

    def test_permissions(self):
        qualifier = Qualifier.objects.create(
            account=self.account,
            name="master",
            )

        # Setting value permissions
        qualifier.set_permission("crm_business", True)
        qualifier.set_permission("crm_person", False)
        qualifier.set_permission("crm_locations_limit", 5)

        # Getting valid permissions
        self.assertTrue(qualifier.get_permission("crm_business"))
        self.assertFalse(qualifier.get_permission("crm_person"))
        self.assertTrue(qualifier.get_permission("crm_locations_limit", 3))
        self.assertFalse(qualifier.get_permission("crm_locations_limit", 10))

        # Existing permission
        qualifier.set_permission("crm_locations_limit", 12)
        self.assertTrue(qualifier.get_permission("crm_locations_limit", 10))

        # Setting invalid permissions
        try:
            qualifier.set_permission("crm_business", "mario")
        except TypeError as e:
            self.assertEqual(str(e), "Boolean feature requires boolean value.")

        try:
            qualifier.set_permission("crm_locations_limit", None)
        except TypeError as e:
            self.assertEqual(str(e), "Limit feature requires integer value.")

        # Getting invalid permissions
        try:
            self.assertFalse(qualifier.get_permission("crm_permission"))
        except Exception as e:
            self.assertTrue(isinstance(e, Feature.DoesNotExist))


class TestWebhook(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name="T Dispatch",
            )
        PusherWebhook._test["mode"] = True
        PusherWebhook._test["pool"] = []

    def tearDown(self):
        Account.objects.all().delete()
        responses.reset()

    def test_pusher(self):
        webhook = self.account.webhooks.create(
            type="pusher",
            param1="123456",
            param2="abcedf",
            param3="UVWXYZ",
            )

        # Pusher is called when feature is changed
        # ... created
        feature1 = self.account.features.create(
            name="crm_business",
            permission_type=Feature.TYPE_BOOLEAN,
            )
        self.assertEqual(len(PusherWebhook._test["pool"]), 1)
        self.assertEqual(PusherWebhook._test["pool"][-1]["account"], self.account.shortcode)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {})

        # Pusher client
        self.assertEqual(PusherWebhook._test["pool"][-1]["client"].app_id, "123456")
        self.assertEqual(PusherWebhook._test["pool"][-1]["client"].key, "abcedf")
        self.assertEqual(PusherWebhook._test["pool"][-1]["client"].secret, "UVWXYZ")

        # New qualifier create
        qualifier = Qualifier.objects.create(
            account=self.account,
            name="master",
            )
        self.assertEqual(len(PusherWebhook._test["pool"]), 3)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {u'crm_business': False}})

        # Qualifier setting permission
        qualifier.set_permission("crm_business", True)
        self.assertEqual(len(PusherWebhook._test["pool"]), 4)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {u'crm_business': True}})

        # ... updated and permission level "all" (instead of "per qualifier")
        feature1.permission_level = Feature.LEVEL_ALL
        feature1.save()
        self.assertEqual(len(PusherWebhook._test["pool"]), 5)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {u'crm_business': False}})

        # ... deleted
        feature1.delete()
        self.assertEqual(len(PusherWebhook._test["pool"]), 7) # Because of dependencies deletion
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {}})

        # New feature - testing level all permission value
        self.feature2 = self.account.features.create(
            name="crm_person",
            permission_type=Feature.TYPE_BOOLEAN,
            boolean_permission=True,
            )
        self.assertEqual(len(PusherWebhook._test["pool"]), 9)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {u'crm_person': True}})

        # ... level "all" with permission value
        self.feature2.permission_level = Feature.LEVEL_ALL
        self.feature2.save()
        self.assertEqual(len(PusherWebhook._test["pool"]), 10)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {u'crm_person': True}})

        # New feature - type limit
        self.feature3 = self.account.features.create(
            name="crm_locations_limit",
            permission_type=Feature.TYPE_LIMIT,
            limit_permission=10,
            )
        self.assertEqual(len(PusherWebhook._test["pool"]), 12)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {
            u'crm_locations_limit': 10, 
            u'crm_person': True,
            }})

        qualifier.set_permission("crm_locations_limit", 5)
        self.assertEqual(len(PusherWebhook._test["pool"]), 13)
        self.assertEqual(PusherWebhook._test["pool"][-1]["permissions"], {u'master': {
            u'crm_locations_limit': 5, 
            u'crm_person': True,
            }})

    @responses.activate
    def test_url(self):
        responses.add(
            method="POST",
            url="http://url.test/?arg1=123",
            body='{"result": "ok"}',
            match_querystring=True,
            )

        webhook = self.account.webhooks.create(
            type="url",
            param1="http://url.test/?arg1=123",
            )

        # Pusher is called when feature is changed
        # ... created
        feature1 = self.account.features.create(
            name="crm_business",
            permission_type=Feature.TYPE_BOOLEAN,
            permission_level=Feature.LEVEL_ALL,
            boolean_permission=True
            )
        qualifier = Qualifier.objects.create(
            account=self.account,
            name="master",
            )
        self.assertEqual(responses.calls[0].request.url, "http://url.test/?arg1=123")
        self.assertEqual(json.loads(responses.calls[0].request.body), {
            "account": self.account.shortcode,
            "permissions": {},
            })
        self.assertEqual(responses.calls[0].request.headers['content-type'], "text/javascript")


class TestAdmin(TestCase):
    def setUp(self):
        self.cl = Client()

    def test_account(self):
        resp = self.cl.get("/admin/toggle/account")
        self.assertEqual(resp.status_code, 301)

    def test_qualifier(self):
        resp = self.cl.get("/admin/toggle/qualifier")
        self.assertEqual(resp.status_code, 301)


class TestApi(ResourceTestCase):
    def setUp(self):
        super(TestApi, self).setUp()
        self.account = Account.objects.create(
            name="T Dispatch",
            )
        self.feature1 = self.account.features.create(
            name="crm_business",
            permission_type=Feature.TYPE_BOOLEAN,
            )
        self.feature2 = self.account.features.create(
            name="crm_person",
            permission_type=Feature.TYPE_BOOLEAN,
            )
        self.feature3 = self.account.features.create(
            name="crm_locations_limit",
            permission_type=Feature.TYPE_LIMIT,
            )
        self.qualifier1 = Qualifier.objects.create(
            account=self.account,
            name="master",
            )
        self.qualifier2 = Qualifier.objects.create(
            account=self.account,
            name="basic",
            )

    def tearDown(self):
        Account.objects.all().delete()
        super(TestApi, self).tearDown()

    def get_credentials(self):
        return "ApiKey {0}".format(self.account.api_key)

    def test_invalid_authentication(self):
        resp = self.api_client.get("/api/v1/feature/", authentication="Mary Johnson")
        self.assertHttpUnauthorized(resp)

        resp = self.api_client.get("/api/v1/feature/", authentication="ApiKey mario")
        self.assertHttpUnauthorized(resp)

    def test_features_invalid_name(self):
        # Add
        resp = self.api_client.post('/api/v1/feature/', format='json', data={
            "name": "crm.EXPORT_CSV",
            }, authentication=self.get_credentials())
        self.assertHttpBadRequest(resp)

    def test_features(self):
        # Add
        resp = self.api_client.post('/api/v1/feature/', format='json', data={
            "name": "crm_export_csv",
            }, authentication=self.get_credentials())
        self.assertHttpCreated(resp)
        feature = Feature.objects.get(name="crm_export_csv")
        self.assertEqual(feature.account, self.account)

        # Get
        resp = self.api_client.get('/api/v1/feature/crm_export_csv/', format='json',
                authentication=self.get_credentials())
        self.assertHttpOK(resp)
        data = json.loads(resp.content)
        self.assertEqual(set(data.keys()), set([u'name', u'creation', u'permission_type',
            u'boolean_permission', u'limit_permission', u'permission_level', u'id',
            u'resource_uri']))
        self.assertEqual(data["permission_type"], "boolean")
        self.assertEqual(data["permission_level"], "qualifier")

        # Update
        resp = self.api_client.put('/api/v1/feature/crm_export_csv/', format='json', data={
            "permission_level": "all",
            }, authentication=self.get_credentials())
        self.assertHttpOK(resp)
        self.assertEqual(self.account.features.get(name="crm_export_csv").permission_level, "all")

        # List
        resp = self.api_client.get('/api/v1/feature/', format='json',
            authentication=self.get_credentials())
        self.assertHttpOK(resp)
        data = json.loads(resp.content)
        self.assertEqual(len(data["objects"]), 4)

        # Delete
        resp = self.api_client.delete('/api/v1/feature/crm_export_csv/', format='json',
            authentication=self.get_credentials())
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.account.features.filter(name="crm_export_csv").count(), 0)

    def test_qualifiers(self):
        # Add
        resp = self.api_client.post('/api/v1/qualifier/', format='json', data={
            "name": "premium",
            }, authentication=self.get_credentials())
        self.assertHttpCreated(resp)
        qualifier = Qualifier.objects.get(name="premium")
        self.assertEqual(qualifier.account, self.account)

        # Get
        resp = self.api_client.get('/api/v1/qualifier/premium/', format='json',
                authentication=self.get_credentials())
        self.assertHttpOK(resp)
        data = json.loads(resp.content)
        self.assertEqual(set(data.keys()), set([u'name', u'creation', u'id',
            "permissions", u'resource_uri']))

        # Update
        resp = self.api_client.put('/api/v1/qualifier/premium/', format='json', data={
            "name": "PREMIUM",
            }, authentication=self.get_credentials())
        self.assertHttpOK(resp)
        self.assertEqual(self.account.qualifiers.filter(name="premium").count(), 1)

        # List
        resp = self.api_client.get('/api/v1/qualifier/', format='json',
            authentication=self.get_credentials())
        self.assertHttpOK(resp)
        data = json.loads(resp.content)
        self.assertEqual(len(data["objects"]), 3)

        # Delete
        resp = self.api_client.delete('/api/v1/qualifier/premium/', format='json',
            authentication=self.get_credentials())
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.account.qualifiers.filter(name="premium").count(), 0)

    def test_permissions(self):
        # Set
        resp = self.api_client.post('/api/v1/permissions/', format='json', data={
            "permissions": {
                "master": {
                    "crm_business": True,
                    "crm_person": False,
                    "crm_locations_limit": 12,
                    },
                },
            }, authentication=self.get_credentials())

        self.assertHttpCreated(resp)
        self.assertEqual(json.loads(resp.content), {
            u'resource_uri': u'',
            u'permissions': {
                u'master': {
                    u'crm_business': True,
                    u'crm_person': False,
                    u'crm_locations_limit': 12,
                    },
                u'basic': {
                    u'crm_business': False,
                    u'crm_person': False,
                    u'crm_locations_limit': 0,
                    },
                },
            })
        self.assertTrue(self.qualifier1.get_permission("crm_business"))
        self.assertFalse(self.qualifier1.get_permission("crm_person"))
        self.assertEqual(self.qualifier1.get_permission_value("crm_locations_limit"), 12)

        # Get all permissions for account
        resp = self.api_client.get('/api/v1/permissions/', format='json',
            authentication=self.get_credentials())
        self.assertHttpOK(resp)
        self.assertEqual(json.loads(resp.content), {
            'permissions': {
                'master': {
                    'crm_business': True,
                    'crm_person': False,
                    'crm_locations_limit': 12,
                    },
                u'basic': {
                    u'crm_business': False,
                    u'crm_person': False,
                    u'crm_locations_limit': 0,
                    },
                },
            })

        # Get all permissions for qualifier
        resp = self.api_client.get('/api/v1/permissions/?qualifier=master', format='json',
            authentication=self.get_credentials())
        self.assertHttpOK(resp)
        self.assertEqual(json.loads(resp.content), {
            'permissions': {
                'master': {
                    'crm_business': True,
                    'crm_person': False,
                    'crm_locations_limit': 12,
                    },
                },
            })

