from os import path
from unittest import mock
from unittest.mock import MagicMock

import ldap3
import pytest
import sshpubkeys
from click.testing import CliRunner
from pytest_mock import mocker  # noqa: F401

import ldap_tools.key
from ldap_tools.client import Client
from ldap_tools.key import API as KeyApi
from ldap_tools.key import CLI as KeyCli
from ldap_tools.user import API as UserApi


def describe_key():
    username = 'test.user'
    fixture_path = path.join(path.dirname(__file__), 'fixtures')
    filename = path.join(fixture_path, 'two_key_user')
    distinguished_name = 'cn=test.user,ou=People,dc=test,dc=org'
    ldap_entry = [[[
        distinguished_name, {
            'objectClass': [
                b'top', b'posixAccount', b'shadowAccount', b'inetOrgPerson',
                b'organizationalPerson', b'person', b'ldapPublicKey'
            ]
        }
    ]]]

    def describe_commandline_operations():
        runner = CliRunner()  # initialize commandline runner

        def it_adds_a_key(mocker):  # noqa: F811
            mocker.patch('ldap_tools.key.API.add', return_value=None)
            mocker.patch(
                'ldap_tools.client.Client.prepare_connection',
                return_value=None)

            runner.invoke(
                KeyCli.key,
                ['add', '--username', username, '--filename', filename])

            ldap_tools.key.API.add.assert_called_once_with(
                username, mock.ANY, filename)

        def it_removes_a_key(mocker):  # noqa: F811
            mocker.patch('ldap_tools.key.API.remove', return_value=None)
            mocker.patch(
                'ldap_tools.client.Client.prepare_connection',
                return_value=None)

            runner.invoke(KeyCli.key, [
                'remove', '--username', username, '--filename', filename,
                '--force'
            ])

            ldap_tools.key.API.remove.assert_called_once_with(
                username, mock.ANY, filename, True)

    def describe_api_calls():
        client = Client()
        client.prepare_connection = MagicMock()

        def describe_key_addition():
            client.modify = MagicMock()
            user_api = UserApi(client)
            user_api.find = MagicMock(return_value=ldap_entry)
            key_api = KeyApi(client)

            def it_calls_the_client():
                pytest.xfail(
                    reason='Need to learn how to mock user.entry_dn')
                client.modify.reset_mock()
                filename = path.join(fixture_path, 'single_key_user')
                key_api.add(username, user_api, filename)
                client.modify.assert_called_once_with(distinguished_name,
                                                      mock.ANY)

            def it_raises_error_on_bad_key():
                pytest.xfail(
                    reason='Need to learn how to mock user.entry_dn')
                filename = path.join(fixture_path, 'invalid_user_key')

                with pytest.raises(sshpubkeys.exceptions.MalformedDataError):
                    key_api.add(username, user_api, filename)

            def it_raises_error_on_bad_object():
                pytest.xfail(
                    reason='Need to learn how to mock user.entry_dn')
                filename = path.join(fixture_path, 'single_key_user')
                ldap_entry = [[
                    distinguished_name, {
                        'objectClass': [
                            b'top', b'posixAccount', b'shadowAccount',
                            b'inetOrgPerson', b'organizationalPerson',
                            b'person'
                        ]
                    }
                ]]
                user_api.find = MagicMock(return_value=ldap_entry)

                with pytest.raises(
                        ldap3.core.exceptions.LDAPNoSuchAttributeResult):
                    key_api.add(username, user_api, filename)

        def it_removes_key_from_user(mocker):  # noqa: F811
            pytest.xfail(
                reason='Need to learn how to mock user.entry_dn')
            client.modify = MagicMock()
            client.search = MagicMock()
            user_api = UserApi(client)
            user_api.find = MagicMock(return_value=ldap_entry)
            key_api = KeyApi(client)

            with open(path.join(fixture_path, 'two_key_user'),
                      'r') as FILE:  # get current keys
                mocker.patch.object(
                    key_api,
                    '_API__current_keys',
                    return_value=FILE.read().splitlines())

            filename = path.join(fixture_path, 'delete_user_key')

            key_api.remove(username, user_api, filename, True)
            client.modify.assert_called_once_with(distinguished_name, mock.ANY)

        def describe_get_keys_from_ldap():
            client.search = MagicMock()
            key_api = KeyApi(client)

            def it_filters_with_username():
                client.search.reset_mock()
                filter = ['(sshPublicKey=*)', '(uid={})'.format(username)]
                key_api.get_keys_from_ldap(username)

                client.search.assert_any_call(filter, ['uid', 'sshPublicKey'])

            def it_filters_without_username():
                client.search.reset_mock()
                filter = ['(sshPublicKey=*)']
                key_api.get_keys_from_ldap()

                client.search.assert_called_once_with(filter,
                                                      ['uid', 'sshPublicKey'])
