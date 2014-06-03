from django.conf.urls import patterns, include, url

urlpatterns = patterns('bipolar_server.toggle.views',
    url(r'^$', "index", name="index"),
    url(r'^accounts/add/$', "account_add", name="account_add"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/$', "account_view", name="account_view"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/features/add/$', "feature_form", name="feature_add"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/features/(?P<feature_pk>\d+)/$', "feature_form", name="feature_edit"),
    #url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/features/(?P<feature_pk>\d+)/delete/$', "feature_delete", name="feature_delete"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/qualifiers/add/$', "qualifier_form", name="qualifier_add"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/qualifiers/(?P<qualifier_pk>\d+)/$', "qualifier_form", name="qualifier_edit"),
    #url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/qualifiers/(?P<qualifier_pk>\d+)/delete/$', "qualifier_delete", name="qualifier_delete"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/webhooks/add/$', "webhook_form", name="webhook_add"),
    url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/webhooks/(?P<webhook_pk>\d+)/$', "webhook_form", name="webhook_edit"),
    #url(r'^accounts/(?P<shortcode>[A-Z0-9]{8})/webhooks/(?P<webhook_pk>\d+)/delete/$', "webhook_delete", name="webhook_delete"),
    )

urlpatterns += patterns('bipolar_server.toggle.auth',
    url(r'^signup-email/', 'signup_email'),
    url(r'^email-sent/', 'validation_sent'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'ajax_auth', name='ajax-auth'),
    url(r'^email/$', 'require_email', name='require_email'),
)

