from .plugin import CredentialPlugin

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from delinea.secrets.vault import PasswordGrantAuthorizer, SecretsVault

dsv_inputs = {
    'fields': [
        {
            'id': 'tenant',
            'label': _('Tenant'),
            'help_text': _('The tenant e.g. "ex" when the URL is https://ex.secretsvaultcloud.com'),
            'type': 'string',
        },
        {
            'id': 'tld',
            'label': _('Top-level Domain (TLD)'),
            'help_text': _('The TLD of the tenant e.g. "com" when the URL is https://ex.secretsvaultcloud.com'),
            'choices': ['ca', 'com', 'com.au', 'eu'],
            'default': 'com',
        },
        {
            'id': 'client_id',
            'label': _('Client ID'),
            'type': 'string',
        },
        {
            'id': 'client_secret',
            'label': _('Client Secret'),
            'type': 'string',
            'secret': True,
        },
    ],
    'metadata': [
        {
            'id': 'path',
            'label': _('Secret Path'),
            'type': 'string',
            'help_text': _('The secret path e.g. /test/secret1'),
        },
        {
            'id': 'secret_field',
            'label': _('Secret Field'),
            'help_text': _('The field to extract from the secret'),
            'type': 'string',
        },
    ],
    'required': ['tenant', 'client_id', 'client_secret', 'path', 'secret_field'],
}

if settings.DEBUG:
    dsv_inputs['fields'].append(
        {
            'id': 'url_template',
            'label': _('URL template'),
            'type': 'string',
            'default': 'https://{}.secretsvaultcloud.{}',
        }
    )


def dsv_backend(**kwargs):
    tenant_name = kwargs['tenant']
    tenant_tld = kwargs.get('tld', 'com')
    tenant_url_template = kwargs.get('url_template', 'https://{}.secretsvaultcloud.{}')
    client_id = kwargs['client_id']
    client_secret = kwargs['client_secret']
    secret_path = kwargs['path']
    secret_field = kwargs['secret_field']

    tenant_url = tenant_url_template.format(tenant_name, tenant_tld.strip("."))

    authorizer = PasswordGrantAuthorizer(tenant_url, client_id, client_secret)
    dsv_secret = SecretsVault(tenant_url, authorizer).get_secret(secret_path)

    return dsv_secret['data'][secret_field]


dsv_plugin = CredentialPlugin(name='Thycotic DevOps Secrets Vault', inputs=dsv_inputs, backend=dsv_backend)
