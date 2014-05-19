from django.contrib import admin

from toggle.models import Account, Feature, Qualifier, QualifierPermission


class InlineAccountFeature(admin.TabularInline):
    model = Feature
    extra = 0


class AdminAccount(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [InlineAccountFeature]


class InlineQualifierPermission(admin.TabularInline):
    model = QualifierPermission
    extra = 0


class AdminQualifier(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("account",)
    inlines = [InlineQualifierPermission]


admin.site.register(Account, AdminAccount)
admin.site.register(Qualifier, AdminQualifier)

