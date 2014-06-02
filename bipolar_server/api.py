from tastypie.api import Api

from bipolar_server.toggle.api import FeatureResource
from bipolar_server.toggle.api import QualifierResource
from bipolar_server.toggle.api import PermissionsResource

v1_api = Api(api_name='v1')
v1_api.register(FeatureResource())
v1_api.register(QualifierResource())
v1_api.register(PermissionsResource())
