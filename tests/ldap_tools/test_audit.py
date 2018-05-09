from click.testing import CliRunner
from pytest_mock import mocker  # noqa: F401

import ldap_tools
from ldap_tools.audit import CLI as AuditCli


def describe_audit():
    def describe_commandline_operations():
        runner = CliRunner()

        def it_lists_groups_by_user(mocker):  # noqa: F811
            mocker.patch('ldap_tools.audit.API.by_user', return_value=None)
            mocker.patch(
                'ldap_tools.client.Client.prepare_connection',
                return_value=None)

            runner.invoke(AuditCli.audit, ['by_user'])
            ldap_tools.audit.API.by_user.assert_called_once_with()

        def it_lists_users_by_group(mocker):  # noqa: F811
            mocker.patch('ldap_tools.audit.API.by_group', return_value=None)
            mocker.patch(
                'ldap_tools.client.Client.prepare_connection',
                return_value=None)

            runner.invoke(AuditCli.audit, ['by_group'])
            ldap_tools.audit.API.by_group.assert_called_once_with()

    def describe_api_calls():
        pass  # no testable methods implemented

    def describe_utility_methods():
        pass
