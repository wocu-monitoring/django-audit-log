from unittest import mock

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from django_audit_log.rest_framework.viewsets import AuditLogReadOnlyViewSet, AuditLogViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response


class DynamicReadOnlyViewSet(AuditLogReadOnlyViewSet):
    """
    A base ViewSet used for testing.

    All named arguments will be added as an attribute to the object.
    This allows us to dynamically determine the behaviour while still
    using a single class (instead of having to recreate this class
    for each test).

    Note that it is also possible to pass methods to kwargs if you
    want to override a class method (e.g. get_queryset()).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class DynamicViewSet(DynamicReadOnlyViewSet, AuditLogViewSet):
    pass


class TestAuditLogReadOnlyViewset(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_lookup_kwargs_lookup_field(self):
        view_set = DynamicReadOnlyViewSet(lookup_field='key', kwargs={'key': 'value'})
        self.assertEqual(view_set._get_lookup_kwargs(), {'key': 'value'})

    def test_get_lookup_kwargs_lookup_url_kwargs(self):
        view_set = DynamicReadOnlyViewSet(kwargs={'test': 'value'}, lookup_field='key', lookup_url_kwarg='test')
        self.assertEqual(view_set._get_lookup_kwargs(), {'key': 'value'})

    def test_get_filter_kwargs_without_search_backend(self):
        view_set = DynamicReadOnlyViewSet()
        request = self.factory.get('/')
        self.assertEqual(view_set._get_filter_kwargs(request), {"[]": []})

    def test_get_filter_kwargs_with_search_backend(self):
        view_set = DynamicReadOnlyViewSet(filter_backends=[SearchFilter], search_fields=['email'])
        request = self.factory.get('/')
        request.query_params = {'search': 'test'}
        self.assertEqual(view_set._get_filter_kwargs(request), {"['email']": ['test']})

    def test_get_filter_kwargs_with_other_backend(self):
        view_set = DynamicReadOnlyViewSet(filter_backends=[OrderingFilter], ordering_fields=['email'])
        request = self.factory.get('/')
        self.assertEqual(view_set._get_filter_kwargs(request), {"[]": []})

    def test_get_model_name_queryset(self):
        self.assertEqual(AuditLogReadOnlyViewSet()._get_model_name(User.objects.all()), 'User')

    def test_get_model_name_method(self):
        view_set = DynamicReadOnlyViewSet(get_queryset=lambda: User.objects.all())
        self.assertEqual(view_set._get_model_name(), 'User')

    def test_get_model_name_attr(self):
        view_set = DynamicReadOnlyViewSet(queryset=User.objects.all())
        self.assertEqual(view_set._get_model_name(), 'User')

    @mock.patch('rest_framework.mixins.RetrieveModelMixin.retrieve')
    def test_retrieve(self, mocked_retrieve):
        mocked_retrieve.return_value = Response(data='test')
        view_set = DynamicReadOnlyViewSet(queryset=User.objects.all(), kwargs={'pk': '1'}, lookup_field='pk')
        request = self.factory.get('/')

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.retrieve(request)
            self.assertEqual(response.data, 'test')
            mocked_logger.set_filter.assert_called_with(object_name='User', kwargs={'pk': '1'})
            mocked_logger.set_results.assert_called_with('test')
            mocked_logger.info.assert_called_with("Retrieve User")

    @mock.patch('rest_framework.mixins.RetrieveModelMixin.retrieve')
    def test_retrieve_missing_audit_log(self, mocked_retrieve):
        mocked_retrieve.return_value = Response(data='test')
        view_set = DynamicViewSet(queryset=User.objects.all())
        request = self.factory.get('/')
        response = view_set.retrieve(request)
        self.assertEqual(response.data, 'test')

    @mock.patch('rest_framework.mixins.ListModelMixin.list')
    def test_list_without_results_with_filter(self, mocked_list):
        mocked_list.return_value = Response(data=['test1', 'test2'])
        view_set = DynamicReadOnlyViewSet(
            queryset=User.objects.all(), filter_backends=[SearchFilter], search_fields=['email'])
        request = self.factory.get('/')
        request.query_params = {'search': 'test'}

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.list(request)
            self.assertEqual(response.data, ['test1', 'test2'])
            mocked_logger.set_filter.assert_called_with(object_name='User', kwargs={"['email']": ['test']})
            mocked_logger.info.assert_called_with('List User')
            mocked_logger.set_results.assert_not_called()

    @mock.patch('rest_framework.mixins.ListModelMixin.list')
    def test_list_with_results_without_filter(self, mocked_list):
        mocked_list.return_value = Response(data=['test1', 'test2'])
        view_set = DynamicReadOnlyViewSet(queryset=User.objects.all(), audit_log_list_response=True)
        request = self.factory.get('/')

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.list(request)
            self.assertEqual(response.data, ['test1', 'test2'])
            mocked_logger.set_filter.assert_called_with(object_name='User', kwargs={"[]": []})
            mocked_logger.info.assert_called_with('List User')
            mocked_logger.set_results.assert_called_with(['test1', 'test2'])

    @mock.patch('rest_framework.mixins.ListModelMixin.list')
    def test_list_missing_audit_log(self, mocked_list):
        mocked_list.return_value = Response(data=['test1', 'test2'])
        view_set = DynamicViewSet(queryset=User.objects.all())
        request = self.factory.get('/')
        response = view_set.list(request)
        self.assertEqual(response.data, ['test1', 'test2'])


class TestAuditLogViewSet(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch('rest_framework.mixins.CreateModelMixin.create')
    def test_create(self, mocked_create):
        mocked_create.return_value = Response(data='test', status=201, headers=[])
        view_set = DynamicViewSet(queryset=User.objects.all())
        request = self.factory.get('/')

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.create(request)
            self.assertEqual(response.data, 'test')
            mocked_logger.set_results.assert_called_with('test')
            mocked_logger.info.assert_called_with("Created User object")

    @mock.patch('rest_framework.mixins.CreateModelMixin.create')
    def test_create_missing_audit_log(self, mocked_create):
        mocked_create.return_value = Response(data='test', status=201, headers=[])
        view_set = DynamicViewSet(queryset=User.objects.all())
        request = self.factory.get('/')
        response = view_set.create(request)
        self.assertEqual(response.data, 'test')

    @mock.patch('rest_framework.mixins.UpdateModelMixin.update')
    def test_update(self, mocked_update):
        mocked_update.return_value = Response(data='test')
        view_set = DynamicViewSet(queryset=User.objects.all(), kwargs={'pk': '1'}, lookup_field='pk')
        request = self.factory.get('/')

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.update(request)
            self.assertEqual(response.data, 'test')
            mocked_logger.set_filter.assert_called_with(object_name='User', kwargs={'pk': '1'})
            mocked_logger.set_results.assert_called_with('test')
            mocked_logger.info.assert_called_with("Update of User")

    @mock.patch('rest_framework.mixins.UpdateModelMixin.update')
    def test_update_missing_audit_log(self, mocked_update):
        mocked_update.return_value = Response(data='test')
        view_set = DynamicViewSet(queryset=User.objects.all(), kwargs={}, lookup_field='pk')
        request = self.factory.get('/')
        response = view_set.update(request)
        self.assertEqual(response.data, 'test')

    @mock.patch('rest_framework.mixins.DestroyModelMixin.destroy')
    def test_destroy(self, mocked_destroy):
        mocked_destroy.return_value = Response(status=204)
        view_set = DynamicViewSet(queryset=User.objects.all(), kwargs={'pk': '1'}, lookup_field='pk')
        request = self.factory.get('/')

        with mock.patch('django_audit_log.logger.AuditLogger') as mocked_logger:
            request.audit_log = mocked_logger
            response = view_set.destroy(request)
            self.assertEqual(response.data, None)
            self.assertEqual(response.status_code, 204)
            mocked_logger.set_filter.assert_called_with(object_name='User', kwargs={'pk': '1'})
            mocked_logger.set_results.assert_called_with(None)
            mocked_logger.info.assert_called_with("Destroy User")

    @mock.patch('rest_framework.mixins.DestroyModelMixin.destroy')
    def test_destroy_missing_audit_log(self, mocked_destroy):
        mocked_destroy.return_value = Response(status=204)
        view_set = DynamicViewSet(queryset=User.objects.all(), kwargs={}, lookup_field='pk')
        request = self.factory.get('/')
        response = view_set.destroy(request)
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, 204)
