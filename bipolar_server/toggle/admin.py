from django.contrib import admin

from models import Account
from models import Feature
from models import Qualifier
from models import QualifierPermission
from models import Webhook
from models import UserAccount


class InlineAccountFeature(admin.TabularInline):
    model = Feature
    extra = 0


class InlineAccountWebhook(admin.TabularInline):
    model = Webhook
    extra = 0


class InlineUserAccount(admin.TabularInline):
    model = UserAccount
    extra = 0


class AdminAccount(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [InlineAccountFeature, InlineAccountWebhook, InlineUserAccount]
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

