import random
import jellyfish
from django.db import models
from django.utils.crypto import get_random_string

from webhooks import send_to_webhook


class Account(models.Model):
    name = models.CharField(max_length=50)
    creation = models.DateTimeField(auto_now_add=True, db_index=True)
    shortcode = models.CharField(max_length=8, unique=True, blank=True)
    api_key = models.CharField(max_length=32, unique=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.shortcode:
            self.shortcode = jellyfish.metaphone(self.name.upper().replace(" ", ""))[:4] +\
                             str(random.randint(0, 9999)).zfill(4)

        if not self.api_key:
            self.api_key = get_random_string(32)

        return super(Account, self).save(*args, **kwargs)

    def format_all_permissions(self):
        data = {
            "account": self.shortcode,
            "permissions": {
                },
            }
        
        for qualifier in self.qualifiers.order_by("name"):
            d = data["permissions"][qualifier.name] = {}

            for feature in self.features.order_by("name"):
                d[feature.name] = qualifier.get_permission_value(feature.name)

        return data

    def send_to_webhooks(self):
        if not self.webhooks.count():
            return

        data = self.format_all_permissions()

        for webhook in self.webhooks.all():
            send_to_webhook(data, webhook)

    def get_default_permissions(self):
        permissions = {}
        for feature in self.features.order_by("name"):
            if feature.permission_type == Feature.TYPE_BOOLEAN:
                permissions[feature.name] = bool(feature.boolean_permission)
            elif feature.permission_type == Feature.TYPE_LIMIT:
                permissions[feature.name] = feature.limit_permission or 0
        return permissions


class Feature(models.Model):
    TYPE_BOOLEAN = "boolean"
    TYPE_LIMIT = "limit"
    TYPES = (
        (TYPE_BOOLEAN, "Boolean"),
        (TYPE_LIMIT, "Limit"),
        )

    LEVEL_ALL = "all"
    LEVEL_QUALIFIER = "qualifier"
    LEVELS = (
        (LEVEL_ALL, "All"),
        (LEVEL_QUALIFIER, "Qualifier"),
        )

    account = models.ForeignKey("Account", related_name="features")
    name = models.CharField(max_length=50)
    creation = models.DateTimeField(auto_now_add=True, db_index=True)
    permission_type = models.CharField(
        max_length=10,
        default=TYPE_BOOLEAN,
        choices=TYPES,
        db_index=True,
        )
    permission_level = models.CharField(
        max_length=10,
        default=LEVEL_QUALIFIER,
        choices=LEVELS,
        db_index=True,
        )
    boolean_permission = models.NullBooleanField(null=True, blank=True)
    limit_permission = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(Feature, self).save(*args, **kwargs)


class Qualifier(models.Model):
    account = models.ForeignKey("Account", related_name="qualifiers")
    name = models.CharField(max_length=50)
    creation = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(Qualifier, self).save(*args, **kwargs)

    def get_feature_by_name(self, feature):
        # Get feature by name
        if isinstance(feature, basestring):
            feature = Feature.objects.get(name=feature)

        # Valid feature argument
        if not isinstance(feature, Feature):
            raise TypeError("feature argument must be a name or Feature object")

        return feature

    def set_permission(self, feature, value):
        """
        - feature can be either Feature object or feature name string
        - value can boolean or integer
        """
        # Get feature
        feature = self.get_feature_by_name(feature)

        # Valid arguments' values
        if feature.permission_type == Feature.TYPE_BOOLEAN:
            if value not in (True, False):
                raise TypeError("Boolean feature requires boolean value.")
            
            boolean = value
            limit = None
        elif feature.permission_type == Feature.TYPE_LIMIT:
            if not isinstance(value, int):
                raise TypeError("Limit feature requires integer value.")
            
            boolean = None
            limit = value
        else:
            raise ValueError("Invalid feature permission type '%s'" % feature.permission_type)

        permission, new = self.permissions.get_or_create(
                feature=feature,
                defaults={
                    "boolean_permission": boolean,
                    "limit_permission": limit,
                    }
                )

        if not new:
            permission.boolean_permission = boolean
            permission.limit_permission = limit
            permission.save()

        return permission

    def get_permission_value(self, feature):
        # Get feature
        feature = self.get_feature_by_name(feature)

        # For permission level "all"
        if feature.permission_level == Feature.LEVEL_ALL:
            if feature.permission_type == Feature.TYPE_BOOLEAN:
                return bool(feature.boolean_permission)
            elif feature.permission_type == Feature.TYPE_LIMIT:
                return feature.limit_permission or 0

        # For permission level "qualifier" but non-existing permission
        try:
            permission = self.permissions.get(feature=feature)
        except QualifierPermission.DoesNotExist:
            if feature.permission_type == Feature.TYPE_BOOLEAN:
                return bool(feature.boolean_permission)
            elif feature.permission_type == Feature.TYPE_LIMIT:
                return feature.limit_permission or 0

        # For permission level "qualifier" with a valid permission
        if feature.permission_type == Feature.TYPE_BOOLEAN:
            if permission.boolean_permission is None:
                return bool(feature.boolean_permission)
            else:
                return permission.boolean_permission
        elif feature.permission_type == Feature.TYPE_LIMIT:
            if permission.limit_permission is None:
                return feature.limit_permission or 0
            else:
                return permission.limit_permission

        return False

    def get_permission(self, feature, limit=None):
        if limit is not None and not isinstance(limit, int):
            raise TypeError("limit argument must be None or integer")

        # Get feature
        feature = self.get_feature_by_name(feature)

        value = self.get_permission_value(feature)

        if feature.permission_type == Feature.TYPE_LIMIT:
            return limit <= value
        else:
            return value

    def format_all_permissions(self):
        data = {}
        
        for feature in self.account.features.order_by("name"):
            data[feature.name] = self.get_permission_value(feature.name)

        return data


class QualifierPermission(models.Model):
    class Meta:
        unique_together = (
            ("qualifier", "feature"),
            )

    qualifier = models.ForeignKey("Qualifier", related_name="permissions")
    feature = models.ForeignKey("Feature", related_name="permissions")
    boolean_permission = models.NullBooleanField(null=True, blank=True)
    limit_permission = models.IntegerField(null=True, blank=True)


class Webhook(models.Model):
    TYPE_PUSHER = "pusher"
    TYPE_URL = "url"
    TYPES = (
        (TYPE_PUSHER, "pusher"),
        (TYPE_URL, "url"),
        )

    account = models.ForeignKey("Account", related_name="webhooks")
    type = models.CharField(max_length=10, default=TYPE_PUSHER, choices=TYPES, db_index=True)
    is_active = models.BooleanField(db_index=True, default=True)
    param1 = models.CharField(max_length=100, blank=True) # i.e. Pusher App ID or URL
    param2 = models.CharField(max_length=100, blank=True) # i.e. Pusher Key
    param3 = models.CharField(max_length=100, blank=True) # i.e. Pusher Secret
    param4 = models.CharField(max_length=100, blank=True) # i.e. Pusher Channel
    param5 = models.CharField(max_length=100, blank=True) # i.e. Pusher Event


# Signals

from django.db.models import signals

def send_webhook(instance, sender, **kwargs):
    if sender in (Feature, Qualifier):
        account = instance.account
    elif sender == QualifierPermission:
        account = instance.qualifier.account
    
    account.send_to_webhooks()
signals.post_save.connect(send_webhook, sender=Feature)
signals.post_save.connect(send_webhook, sender=Qualifier)
signals.post_save.connect(send_webhook, sender=QualifierPermission)
signals.post_delete.connect(send_webhook, sender=Feature)
signals.post_delete.connect(send_webhook, sender=Qualifier)
signals.post_delete.connect(send_webhook, sender=QualifierPermission)

