from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from models import Account
from models import UserAccount
from forms import AccountForm
from forms import FeatureForm


@login_required
def index(request):
    return render(request, "index.html")


@login_required
def account_view(request, shortcode):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account
    #account = get_object_or_404(Account, shortcode=shortcode)
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
    # TODO
    return render(request, "qualifier_add.html")


@login_required
def webhook_form(request, shortcode, webhook_pk=None):
    user_account = get_object_or_404(request.user.accounts.all(),
                                     account__shortcode=shortcode)
    account = user_account.account
    # TODO
    return render(request, "webhook_add.html")

