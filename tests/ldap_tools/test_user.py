from unittest import mock
from unittest.mock import MagicMock

import click
import pytest
from click.testing import CliRunner
from pytest_mock import mocker  # noqa: F401

import ldap_tools.exceptions
from ldap_tools.client import Client
from ldap_tools.group import API as GroupApi
from ldap_tools.user import API as UserApi
from ldap_tools.user import CLI as UserCli


def describe_user():  # TODO: change this to use test_key.py format
    first_name = 'Test'
    last_name = 'User'
    username = 'test.user'
    user_type = 'user'
    group_name = 'testGroup'
    ldap_attributes = {'attribute': 'value'}
    runner = CliRunner()  # initialize commandline runner
    client = Client()
    group_api = GroupApi(client)

    def describe_creates_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.user.API.create', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(UserCli.user, [
                    'create', '--name', first_name, last_name, '--type',
                    user_type, '--group', group_name
                ])

                ldap_tools.user.API.create.assert_called_once_with(
                    first_name, last_name, group_name, user_type, mock.ANY)

            def it_raises_exception_on_bad_type(mocker):  # noqa: F811
                mocker.patch('ldap_tools.user.API.create', return_value=None)

                runner.invoke(ldap_tools.user.CLI.user, [
                    'create', '--name', first_name, last_name, '--type',
                    'badType', '--group', group_name
                ])

                assert pytest.raises(click.BadOptionUsage)

        def describe_api():
            def it_assembles_the_current_username(mocker):  # noqa: F811
                client.add = MagicMock()

                user_api = UserApi(client)
                # mock private method __ldap_attr, so we don't have to manage
                # a giant dict that requires mocking many private methods
                client.basedn = 'dc=test,dc=org'
                mocker.patch.object(
                    user_api, '_API__ldap_attr', return_value=ldap_attributes)

                user_api.create(first_name, last_name, group_name, user_type,
                                group_api)
                user_api.ldap_attr = ldap_attributes

                assert user_api.username == 'test.user'

            def it_calls_the_client(mocker):  # noqa: F811
                client.add = MagicMock()

                user_api = UserApi(client)
                # mock private method __ldap_attr, so we don't have to manage
                # a giant dict that requires mocking many private methods
                client.basedn = 'dc=test,dc=org'
                mocker.patch.object(
                    user_api, '_API__ldap_attr', return_value=ldap_attributes)
                mocker.patch.object(
                    UserApi,
                    '_API__object_class',
                    return_value='inetOrgPerson')

                user_api.create(first_name, last_name, group_name, user_type,
                                group_api)
                user_api.ldap_attr = ldap_attributes

                client.add.assert_called_once_with(
                    'uid=test.user,ou=People,dc=test,dc=org', 'inetOrgPerson',
                    ldap_attributes)

    def describe_deletes_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.user.API.delete', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(
                    ldap_tools.user.CLI.user,
                    ['delete', '--username', username, '--type', user_type])

                ldap_tools.user.API.delete.assert_called_once_with(
                    username, user_type)

        def describe_api():
            def it_uses_the_correct_distinguished_name(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.delete', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.load_ldap_config',
                    return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                ldap_tools.client.Client.basedn = 'dc=test,dc=org'

                user_api = UserApi(client)
                user_api.delete(username, user_type)

                ldap_tools.client.Client.delete.assert_called_once_with(
                    'uid=test.user,ou=People,dc=test,dc=org')

    def describe_indexes_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.user.API.index', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(ldap_tools.user.CLI.user, ['index'])

                ldap_tools.user.API.index.assert_called_once_with()

        def describe_api():
            def it_passes_the_correct_filter(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.search', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                user_api = UserApi(client)
                user_api.index()

                ldap_tools.client.Client.search.assert_called_once_with(
                    ["(objectclass=posixAccount)"])

    def describe_shows_user():
        def describe_commandline():
            def it_calls_the_api(mocker):  # noqa: F811
                mocker.patch('ldap_tools.user.API.show', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                runner.invoke(ldap_tools.user.CLI.user,
                              ['show', '--username', username])

                ldap_tools.user.API.show.assert_called_once_with(username)

        def describe_api():
            def it_passes_the_correct_filter(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.search', return_value=None)
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                user_api = UserApi(client)
                user_api.show(username)

                filter = [
                    '(objectclass=posixAccount)', "(uid={})".format(username)
                ]

                ldap_tools.client.Client.search.assert_called_once_with(filter)

    def describe_finds_user():
        def describe_commandline():
            pass  # no methods implemented

        def describe_api():
            def it_finds_a_user(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.search', return_value=['foo'])
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                user_api = UserApi(client)
                user_api.find(username)

                ldap_tools.client.Client.search.assert_called_once_with(
                    ['(uid={})'.format(username)])

            def it_finds_two_users(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.search',
                    return_value=['foo', 'bar'])
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                user_api = UserApi(client)

                with pytest.raises(
                        ldap_tools.exceptions.TooManyResults,
                        message=(
                            "Multiple users found. Please narrow your search."
                        )):
                    user_api.find(username)

            def it_finds_no_users(mocker):  # noqa: F811
                mocker.patch(
                    'ldap_tools.client.Client.search', return_value=[])
                mocker.patch(
                    'ldap_tools.client.Client.prepare_connection',
                    return_value=None)

                user_api = UserApi(client)

                with pytest.raises(
                        ldap_tools.exceptions.NoUserFound,
                        message="User ({}) not found"):
                    user_api.find(username)
