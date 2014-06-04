from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms

from models import Account
from models import UserAccount
from models import QualifierPermission
from forms import AccountForm
from forms import FeatureForm
from forms import WebhookForm
from forms import QualifierForm
from forms import QualifierPermissionFormSet


@login_required
def index(request):
    return render(request, "index.html")


@login_required
def account_view(request, shortcode):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account
    return render(request, "account_view.html", {"account": account})


@login_required
def account_add(request, shortcode=None):
    account = None

    if request.method == "POST":
        form = AccountForm(request.POST, instance=account)

        if form.is_valid():
            account = form.save()
            request.user.accounts.create(
                    account=account,
                    role=UserAccount.ROLE_OWNER,
                    )
            return HttpResponseRedirect(reverse("index"))
    else:
        form = AccountForm(instance=account)

    return render(request, "account_form.html", {"form": form, "account": account})


@login_required
def feature_form(request, shortcode, feature_pk=None):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account

    if feature_pk:
        feature = get_object_or_404(account.features.all(), pk=feature_pk)
    else:
        feature = None

    if request.method == "POST":
        form = FeatureForm(request.POST, instance=feature)

        if form.is_valid():
            feature = form.save(commit=False)
            feature.account = account
            feature.save()

            return HttpResponseRedirect(reverse("account_view", args=(shortcode,)))
    else:
        form = FeatureForm(instance=feature)

    return render(request, "feature_form.html", {"form": form, "feature": feature, "account": account})


@login_required
def qualifier_form(request, shortcode, qualifier_pk=None):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account

    if qualifier_pk:
        qualifier = get_object_or_404(account.qualifiers.all(), pk=qualifier_pk)
        permissions = qualifier.permissions.all()
    else:
        qualifier = None
        permissions = [{
            "feature": feature,
            "boolean_permission": False,
            "limit_permission": None,
            } for feature in account.features.all()]

    if request.method == "POST":
        form = QualifierForm(request.POST, instance=qualifier)

        permissions_formset = QualifierPermissionFormSet(request.POST, queryset=permissions)

        if form.is_valid() and permissions_formset.is_valid():
            qualifier = form.save(commit=False)
            qualifier.account = account
            qualifier.save()

            permissions = permissions_formset.save(commit=False)
            for permission in permissions:
                permission.qualifier = qualifier
                permission.save()

            return HttpResponseRedirect(reverse("account_view", args=(shortcode,)))
    else:
        form = QualifierForm(instance=qualifier)

        if qualifier_pk:
            permissions_formset = QualifierPermissionFormSet(queryset=permissions)
        else:
            permissions_formset = QualifierPermissionFormSet(
                    queryset=QualifierPermission.objects.none(),
                    initial=permissions,
                    )
            permissions_formset.extra = len(permissions)

    return render(request, "qualifier_form.html", {
        "form": form,
        "qualifier": qualifier,
        "account": account,
        "permissions_formset": permissions_formset,
        })


@login_required
def webhook_form(request, shortcode, webhook_pk=None):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account
    if webhook_pk:
        webhook = get_object_or_404(account.webhooks.all(), pk=webhook_pk)
    else:
        webhook = None

    if request.method == "POST":
        form = WebhookForm(request.POST, instance=webhook)

        if form.is_valid():
            webhook = form.save(commit=False)
            webhook.account = account
            webhook.save()

            return HttpResponseRedirect(reverse("account_view", args=(shortcode,)))
    else:
        form = WebhookForm(instance=webhook)

    return render(request, "webhook_form.html", {"form": form, "webhook": webhook, "account": account})

