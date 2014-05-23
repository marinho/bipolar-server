from django.contrib import admin

from toggle.models import Account, Feature, Qualifier, QualifierPermission


class InlineAccountFeature(admin.TabularInline):
    model = Feature
    extra = 0


class AdminAccount(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [InlineAccountFeature]
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

