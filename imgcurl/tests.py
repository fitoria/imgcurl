"""
Tests for my Redis ORM
Adolfo Fitoria <adolfo@fitoria.net>
"""

import time
import redis
import logging

from unittest import TestCase
from models import ConnectionPooler, RedisModel, \
        RedisManager, pickle, ImageLink, ObjectNotFoundError, \
        ObjectNotInitializedError
from app import app
import settings


class ConnectionPoolerTest(TestCase):
    def test_client_creation(self):
        conn_poll = ConnectionPooler()
        self.assertIsInstance(conn_poll.client, redis.Redis)

    def test_client_op(self):
        conn_poll = ConnectionPooler()
        self.assertTrue(conn_poll.client.set('foo', 'bar'))
        self.assertTrue(conn_poll.client.delete('foo'))

class ModelManagerTest(TestCase):
    '''Tests both RedisModel and RedisManager'''
    def _create_sample_instance(self, value="Fooo"):
        return RedisModel(value=value)

    def test_model_save(self):
        obj = self._create_sample_instance()
        self.assertTrue(obj.save())

        conn_poll = ConnectionPooler()
        self.assertEquals(pickle.loads(conn_poll.client.get(obj.key)),
                obj.value)

    def test_model_save_timeout(self):
        '''testing key expiration'''
        manager = RedisManager(RedisModel)
        obj = self._create_sample_instance()
        obj.save(1)
        time.sleep(2)

        self.assertRaises(ObjectNotFoundError, manager.get, obj.key)

    def test_model_delete(self):
        obj = self._create_sample_instance()
        obj.save()
        key = obj.key
        self.assertTrue(obj.delete())

        conn_poll = ConnectionPooler()
        self.assertIsNone(conn_poll.client.get(obj.key))

    def test_manager(self):
        '''Test the manager'''
        manager = RedisManager(RedisModel)
        obj = self._create_sample_instance()
        obj.save()

        fetched_object = manager.get(obj.key)
        self.assertIsInstance(fetched_object, RedisModel)

    def test_model_manager(self):
        '''Tests the model-manager a la django kind of relation'''
        obj = self._create_sample_instance()
        obj.save()

        #FIXME: This test fails
        fetched_obj = RedisModel.objects.get(obj.key)
        self.assertIsInstance(fetched_obj, RedisModel)
        self.assertEquals(obj.key, fetched_obj.key)
        self.assertEquals(obj.value, fetched_obj.value)

    def test_model_persits(self):
        pass

    def test_manager_filter(self):
        pass

    def test_pickling(self):
        '''We create a Python Object and save it to redis with pickle'''
        from datetime import datetime
        test_dict = dict(date=datetime.today(),
                         str_value="foo",
                         float_value=3456.34)

        obj = self._create_sample_instance(test_dict)
        obj.save()
        manager = RedisManager(RedisModel)
        fetched_object = manager.get(obj.key)
        self.assertEquals(fetched_object.value, test_dict)

class FlaskAppTests(TestCase):

    def setUp(self):
        self.image_url1 = 'http://i.imgur.com/WSQBG.jpg'
        self.image_url2 = 'http://i.imgur.com/b71qF.gif'
        self.app = app.test_client()
        self.manager = RedisManager(ImageLink)

        #add one image
        img = ImageLink(key='melon', value=self.image_url1)
        img.save()

    def TearDown(self):
        img = self.manger.get(key)
        img.delete()

    def test_get_image(self):
        rv = self.app.get('/melon')
        self.assertEquals(rv.status_code, 302)
        rv = self.app.get('/foo')
        self.assertEquals(rv.status_code, 404)

    def test_add_image(self):
        rv = self.app.post('/image/add/',
                data={'key': 'iron',
                    'value': self.image_url2,
                    'api_key': settings.API_KEY},
                follow_redirects=True)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals('OK', rv.data)

    def test_del_image(self):
        rv = self.app.post('/image/delete/',
                data={'key': 'iron',
                    'api_key': settings.API_KEY},
                follow_redirects=True)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals('OK', rv.data)

