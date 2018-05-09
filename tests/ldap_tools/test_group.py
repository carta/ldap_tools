from unittest.mock import MagicMock

import click
import ldap3
import pytest
from click.testing import CliRunner
from pytest_mock import mocker  # noqa: F401

import ldap_tools.group
from ldap_tools.client import Client
from ldap_tools.group import API as GroupApi
from ldap_tools.group import CLI as GroupCli


def describe_group():  # TODO: change this to use test_key.py format
    group_name = 'testGroup'
    group_type = 'user'
    username = 'test.user'
    ldap_attributes = {'cn': b'testGroup', 'gidnumber': 99999}
    group_objectclass = ["(objectclass=posixGroup)"]
    runner = CliRunner()
    client = Client()
    client.prepare_connection = MagicMock()
    client.load_ldap_config = MagicMock()
    client.prepare_connection()
    client.basedn = 'dc=test,dc=org'
    client.server = ldap3.Server('my_fake_server')
    client.conn = ldap3.Connection(
        client.server,
        user='cn=test.user,{}'.format(client.basedn),
        password='my_password',
        client_strategy=ldap3.MOCK_SYNC)

    def describe_creates_group():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.group.API.create', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(
                    GroupCli.group,
                    ['create', '--group', group_name, '--type', group_type])

                ldap_tools.group.API.create.assert_called_once_with(
                    group_name, group_type)

            def it_raises_exception_on_bad_type(mocker):  # noqa: F811
                mocker.patch('ldap_tools.group.API.create', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(
                    GroupCli.group,
                    ['create', '--group', group_name, '--type', group_type])

                assert pytest.raises(click.BadOptionUsage)

        def describe_api():
            def it_calls_the_client():
                client.add = MagicMock()
                client.get_max_id = MagicMock(return_value=99999)
                group_objectclass = ['top', 'posixGroup']

                group_api = GroupApi(client)
                # mocker.patch.object(
                #     group_api, '_API__ldap_attr', return_value=ldap_attributes)

                group_api.create(group_name, group_type)
                client.add.assert_called_once_with('cn={},ou=Group,{}'.format(
                    group_name, client.basedn), group_objectclass,
                                                   ldap_attributes)

    def describe_deletes_group():
        def describe_commandline():
            group_api = GroupApi(client)
            group_api.delete = MagicMock()

            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.group.API.delete', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                # We have to force here, otherwise, we get stuck
                # on an interactive prompt
                runner.invoke(GroupCli.group,
                              ['delete', '--group', group_name, '--force'])

                ldap_tools.group.API.delete.assert_called_once_with(group_name)

            def it_exits_on_no_force_no_confirm(mocker):  # noqa: F811
                mocker.patch('ldap_tools.group.API.delete', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)
                mocker.patch('click.confirm', return_value=False)

                # We have to force here, otherwise, we get stuck
                # on an interactive prompt
                result = runner.invoke(GroupCli.group,
                                       ['delete', '--group', group_name])
                assert result.output == "Deletion of {} aborted\n".format(
                    group_name)

        def describe_api():
            def it_calls_the_client():
                client.delete = MagicMock()

                group_api = GroupApi(client)

                group_api.delete(group_name)
                client.delete.assert_called_once_with(
                    'cn={},ou=Group,{}'.format(group_name, client.basedn))

    def describe_adds_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.group.API.add_user', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)
                group_api = GroupApi(client)
                group_api.add_user = MagicMock()

                runner.invoke(GroupCli.group, [
                    'add_user', '--group', group_name, '--username', username
                ])

                ldap_tools.group.API.add_user.assert_called_once_with(
                    group_name, username)

        def describe_api():
            def it_calls_the_client(mocker):  # noqa: F811
                client.modify = MagicMock()

                group_api = GroupApi(client)
                group_api.lookup_id = MagicMock(return_value=99999)

                group_api.add_user(group_name, username)
                client.modify.assert_called_once_with(
                    'cn={},ou=Group,{}'.format(group_name, client.basedn), {
                        'memberUid': [(ldap3.MODIFY_ADD, [username])]
                    })

    def describe_removes_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.group.API.remove_user', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)
                group_api = GroupApi(client)
                group_api.remove_user = MagicMock()

                runner.invoke(GroupCli.group, [
                    'remove_user', '--group', group_name, '--username',
                    username
                ])

                ldap_tools.group.API.remove_user.assert_called_once_with(
                    group_name, username)

        def describe_api():
            def it_calls_the_client():
                client.modify = MagicMock()

                group_api = GroupApi(client)
                group_api.lookup_id = MagicMock(return_value=99999)

                group_api.remove_user(group_name, username)
                client.modify.assert_called_once_with(
                    'cn={},ou=Group,{}'.format(group_name, client.basedn), {
                        'memberUid': [(ldap3.MODIFY_DELETE, [username])]
                    })

    def describe_indexes_groups():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.group.API.index', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)
                group_api = GroupApi(client)
                group_api.index = MagicMock()

                runner.invoke(GroupCli.group, ['index'])

                ldap_tools.group.API.index.assert_called_once_with()

        def describe_api():
            def it_calls_the_client():
                client.search = MagicMock()
                # client.prepare_connection = MagicMock()
                # client.load_ldap_config = MagicMock()

                group_api = GroupApi(client)

                group_api.index()
                client.search.assert_called_once_with(group_objectclass)

    def describe_lookup_id():
        def describe_commandline():
            pass  # not implemented

        def describe_api():
            def it_searches_with_correct_filter():
                pytest.xfail(
                    reason='Need to learn how to mock list.gidNumber.value')
                client.search = MagicMock(return_value=['foo'])

                group_api = GroupApi(client)
                group_api.lookup_id(group_name)
                search_filter = [
                    "(cn={})".format(group_name), "(objectclass=posixGroup)"
                ]
                client.search.assert_called_once_with(search_filter,
                                                      ['gidNumber'])

            def it_raises_exception_on_no_groups_found():
                client.search = MagicMock()
                group_api = GroupApi(client)

                with pytest.raises(
                        ldap_tools.exceptions.NoGroupsFound,
                        message=("No Groups Returned by LDAP.")):
                    group_api.lookup_id(group_name)

            def it_raises_exception_on_multiple_results():
                client.search = MagicMock(return_value=['foo', 'bar'])
                group_api = GroupApi(client)

                with pytest.raises(
                        ldap_tools.exceptions.TooManyResults,
                        message=(
                            "Multiple groups found. Please narrow your search."
                        )):
                    group_api.lookup_id(group_name)
