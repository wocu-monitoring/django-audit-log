from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AuditLogReadOnlyViewSet(ReadOnlyModelViewSet):

    audit_log_list_response = False

    def _get_lookup_kwargs(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        kwargs = getattr(
            self, 'kwargs', {}
        )  # kwargs is set during dispatch(). Prevent possible attribute errors
        return {self.lookup_field: kwargs.get(lookup_url_kwarg, "")}

    def _get_filter_kwargs(self, request):
        search_terms = []
        for backend in list(self.filter_backends):
            if issubclass(backend, SearchFilter):
                search_terms += backend().get_search_terms(request)

        return {str(getattr(self, 'search_fields', [])): search_terms}

    def _get_model_name(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.model.__name__

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if hasattr(request, 'audit_log'):
            model = self._get_model_name()
            request.audit_log.set_filter(
                object_name=model, kwargs=self._get_lookup_kwargs()
            )
            request.audit_log.set_results(response.data)
            request.audit_log.info("Retrieve %s" % model)

        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if hasattr(request, 'audit_log'):
            model = self._get_model_name()
            filter_kwargs = self._get_filter_kwargs(request)
            request.audit_log.set_filter(object_name=model, kwargs=filter_kwargs)
            request.audit_log.info("List %s" % model)

            if self.audit_log_list_response:
                request.audit_log.set_results(response.data)

        return response


class AuditLogViewSet(AuditLogReadOnlyViewSet, ModelViewSet):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if hasattr(request, 'audit_log'):
            model = self._get_model_name()
            request.audit_log.set_results(response.data)
            request.audit_log.info("Created %s object" % model)

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        response = super().update(request, *args, **kwargs)

        if hasattr(request, 'audit_log'):
            model = self._get_model_name()
            message = (
                "Partial update of %s" % model if partial else "Update of %s" % model
            )
            request.audit_log.set_filter(
                object_name=model, kwargs=self._get_lookup_kwargs()
            )
            request.audit_log.set_results(response.data)
            request.audit_log.info(message)

        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)

        if hasattr(request, 'audit_log'):
            model = self._get_model_name()
            request.audit_log.set_filter(
                object_name=model, kwargs=self._get_lookup_kwargs()
            )
            request.audit_log.set_results(response.data)
            request.audit_log.info("Destroy %s" % model)

        return response
