from django.conf.urls import patterns, include, url
from tastypie.resources import Resource, ModelResource, ALL
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication

from toggle.models import Account, Feature, Qualifier


class AccountAuthentication(Authentication):
    def extract_api_key(self, request):
        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            return request.META['HTTP_AUTHORIZATION'].split()[1]
        return None

    def is_authenticated(self, request, **kwargs):
        api_key = self.extract_api_key(request)
        if not api_key:
            return False

        try:
            request.account = Account.objects.get(api_key=api_key)
        except Account.DoesNotExist:
            request.account = None

        return bool(request.account)

    def get_identifier(self, request):
        return request.account.shortcode


class AccountBasedResource(ModelResource):
    def hydrate(self, bundle):
        bundle.obj.account = bundle.request.account
        return bundle

    def get_object_list(self, request):
        qs = super(AccountBasedResource, self).get_object_list(request)
        qs = qs.filter(account=request.account)
        return qs


class FeatureResource(AccountBasedResource):
    class Meta:
        queryset = Feature.objects.all()
        resource_name = 'feature'
        filtering = {
            "name": ALL,
            }
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = AccountAuthentication()
        authorization = Authorization()
        always_return_data = True

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail",
                ),
        ]


class QualifierResource(AccountBasedResource):
    permissions = fields.DictField(null=True)

    class Meta:
        queryset = Qualifier.objects.all()
        resource_name = 'qualifier'
        filtering = {
            "name": ALL,
            }
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = AccountAuthentication()
        authorization = Authorization()
        always_return_data = True

    def dehydrate_permissions(self, bundle):
        return bundle.obj.format_all_permissions()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail",
                ),
        ]


class PermissionsObject(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)


class PermissionsResource(Resource):
    permissions = fields.DictField(null=True)

    class Meta:
        resource_name = 'permissions'
        object_name = "permissions"
        object_class = PermissionsObject
        #list_allowed_methods = ['get']
        #allowed_methods = ['get', "post"]
        authentication = AccountAuthentication()
        authorization = Authorization()
        #include_resource_uri = False
        always_return_data = True

    def obj_create(self, bundle, request = None, **kwargs):
        account = bundle.request.account

        for qualifier_name, permissions in bundle.data["permissions"].items():
            qualifier = account.qualifiers.get(name=qualifier_name)

            for permission_name, value in permissions.items():
                qualifier.set_permission(permission_name, value)

        return bundle

    def detail_uri_kwargs(self, bundle_or_obj):
        return {}

    def get_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        account = base_bundle.request.account

        if request.GET.get("qualifier", None):
            qualifier = account.qualifiers.get(name=request.GET["qualifier"])
            permissions = {
                qualifier.name: qualifier.format_all_permissions(),
                }
        else:
            permissions = account.format_all_permissions()["permissions"]

        return self.create_response(request, {"permissions": permissions})

    def dehydrate_permissions(self, bundle):
        return bundle.request.account.format_all_permissions()["permissions"]

