from django.conf import settings


def toggle(request):
    ret = {}
    ret["BIPOLAR_VERSION"] = settings.BIPOLAR_VERSION
    return ret
