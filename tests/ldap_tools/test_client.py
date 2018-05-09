from unittest.mock import MagicMock

import ldap3
import pytest

import ldap_tools
from ldap_tools.client import Client


def describe_client():
    client = Client()
    client.conn = MagicMock()
    client.basedn = 'dc=test,dc=org'
    distinguished_name = 'cn=test.user,ou=People,dc=test,dc=org'
    object_class = ['inetOrgPerson']
    attributes = {'givenName': 'Test', 'sn': 'User'}

    def it_adds_object_to_ldap():
        client.conn.reset_mock()
        client.add(distinguished_name, object_class, attributes)
        client.conn.add.assert_called_once_with(distinguished_name,
                                                object_class, attributes)

    def describe_client_search():
        client.conn.search = MagicMock()

        def it_searches_with_default_filter_and_attributes():
            pytest.xfail(reason='ideopathic unreliable results')
            search_filter = ["(objectclass=*)"]
            filterstr = "(&{})".format(''.join(search_filter))
            attributes = ['*']
            client.conn.reset_mock()
            client.conn.search.reset_mock()

            client.search(None)
            client.conn.search.assert_any_call(
                search_base=client.basedn,
                search_filter=filterstr,
                search_scope=ldap3.SUBTREE,
                attributes=attributes)

        def it_searches_with_default_attributes_and_custom_filter():
            pytest.xfail(reason='ideopathic unreliable results')
            search_filter = ["(objectclass=top)"]
            filterstr = "(&{})".format(''.join(search_filter))
            attributes = ['*']
            client.conn.reset_mock()
            client.conn.search.reset_mock()

            client.search(search_filter)
            client.conn.search.assert_any_call(
                search_base=client.basedn,
                search_filter=filterstr,
                search_scope=ldap3.SUBTREE,
                attributes=attributes)

        def it_searches_with_default_filter_and_custom_attributes():
            pytest.xfail(reason='ideopathic unreliable results')
            search_filter = ["(objectclass=*)"]
            filterstr = "(&{})".format(''.join(search_filter))
            attributes = ['uid', 'gid']
            client.conn.reset_mock()
            client.conn.search.reset_mock()

            client.search(None, attributes)
            client.conn.search.assert_any_call(
                search_base=client.basedn,
                search_filter=filterstr,
                search_scope=ldap3.SUBTREE,
                attributes=attributes)

    def describe_get_max_id():
        def it_gets_id_of_service_user():
            client.search = MagicMock(return_value=[])
            assert client.get_max_id('user', 'service') == 20000

        def it_gets_id_of_normal_user():
            client.search = MagicMock(return_value=[])
            assert client.get_max_id('user', 'user') == 10000

        def it_raises_error_on_bad_user_type():
            client.search = MagicMock(return_value=[])
            with pytest.raises(
                    ldap_tools.exceptions.InvalidResult,
                    message=("Unknown object type")):
                client.get_max_id('user', 'foo')
