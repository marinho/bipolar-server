from django.contrib import admin

from toggle.models import Account
from toggle.models import Feature
from toggle.models import Qualifier
from toggle.models import QualifierPermission
from toggle.models import Webhook


class InlineAccountFeature(admin.TabularInline):
    model = Feature
    extra = 0


class InlineAccountWebhook(admin.TabularInline):
    model = Webhook
    extra = 0


class AdminAccount(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [InlineAccountFeature, InlineAccountWebhook]
    list_display = ("name", "shortcode", "api_key")


class InlineQualifierPermission(admin.TabularInline):
    model = QualifierPermission
    extra = 0


class AdminQualifier(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("account",)
    inlines = [InlineQualifierPermission]
    list_display = ("name", "account")


admin.site.register(Account, AdminAccount)
admin.site.register(Qualifier, AdminQualifier)

