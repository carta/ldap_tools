"""LDAP Key Management API."""
import os
import sys
from collections import Counter

import click
import ldap3
from sshpubkeys import SSHKey

import ldap_tools.exceptions
from ldap_tools.client import Client
from ldap_tools.user import API as UserApi


class API:
    """Methods to handle LDAP SSH key management."""

    def __init__(self, client):
        """Initialize Key API and LDAP Client."""
        self.client = client

    def add(self, username, user_api, filename=None):
        """
        Add SSH public key to a user's profile.

        Args:
            username: Username to attach SSH public key to
            filename: Filename containing keys to add (optional)

        Raises:
            ldap3.core.exceptions.LDAPNoSuchAttributeResult:
                ldapPublicKey isn't attached to objectClass

        """
        keys = API.__get_keys(filename)
        user = user_api.find(username)[0]
        distinguished_name = user.entry_dn
        if 'ldapPublicKey' not in user.objectClass:
            raise ldap3.core.exceptions.LDAPNoSuchAttributeResult(
                'LDAP Public Key Object Class not found. ' +
                'Please ensure user was created correctly.')
        else:
            for key in list(set(keys)):  # prevents duplicate insertion
                print(key)
                try:
                    SSHKey(key).parse()
                except Exception as err:
                    raise err from None
                else:
                    operation = {'sshPublicKey': [(ldap3.MODIFY_ADD, [key])]}
                    self.client.modify(distinguished_name, operation)

    def remove(self, username, user_api, filename=None, force=False):
        """Remove specified SSH public key from specified user."""
        self.keys = API.__get_keys(filename)
        self.username = username
        user = user_api.find(username)[0]

        if not force:  # pragma: no cover
            self.__confirm()

        for key in self.__delete_keys():
            operation = {'sshPublicKey': [(ldap3.MODIFY_DELETE, [key])]}
            self.client.modify(user.entry_dn, operation)

    def install(self):  # pragma: no cover
        """Install/download ssh keys from LDAP for consumption by SSH."""
        keys = self.get_keys_from_ldap()
        for user, ssh_keys in keys.items():
            user_dir = API.__authorized_keys_path(user)
            if not os.path.isdir(user_dir):
                os.makedirs(user_dir)
            authorized_keys_file = os.path.join(user_dir, 'authorized_keys')
            with open(authorized_keys_file, 'w') as FILE:
                print("\n".join([k.decode() for k in ssh_keys]), file=FILE)

    def get_keys_from_ldap(self, username=None):
        """
        Fetch keys from ldap.

        Args:
            username Username associated with keys to fetch (optional)

        Returns:
            Array of dictionaries in '{username: [public keys]}' format

        """
        result_dict = {}
        filter = ['(sshPublicKey=*)']
        if username is not None:
            filter.append('(uid={})'.format(username))
        attributes = ['uid', 'sshPublicKey']
        results = self.client.search(filter, attributes)
        for result in results:
            result_dict[result.uid.value] = result.sshPublicKey.values
        return result_dict
        # for key, value results[0].items():
        #     yield value

    def __get_key_from_file(filename):
        """
        Get SSH public keys from file.

        Returns:
            List of SSH public keys as read from filename

        """
        with open(filename, 'r') as FILE:
            return FILE.read().splitlines()

    def __get_key_from_commandine():  # pragma: no cover
        """
        Retrieve SSH keys from the command line.

        Returns:
            List of SSH public keys

        """
        return [x.strip() for x in sys.stdin]

    def __get_keys(filename):  # pragma: no cover
        if filename is None:
            return API.__get_key_from_commandine()
        else:
            return API.__get_key_from_file(filename)

    def __keep_keys(self):  # pragma: no cover
        return list(Counter(self.__current_keys()) - Counter(self.keys))

    def __delete_keys(self):
        return list(set(self.__current_keys()) & set(self.keys))

    def __unknown_keys(self):  # pragma: no cover
        return list(Counter(self.keys) - Counter(self.__current_keys()))

    def __current_keys(self):  # pragma: no cover
        return [i.decode() for i in self.get_keys_from_ldap(self.username)[self.username]]

    def __confirm(self):  # pragma: no cover
        print('Please confirm the following operations:')
        print("Keep these keys:\n\n", "\t {}\n\n".format(self.__keep_keys()))
        print("Delete these keys:\n\n", "\t {}\n\n".format(
            self.__delete_keys()))
        print("Ignore these keys (not found in LDAP for {}):\n\n".format(
            self.username), "\t {}\n\n".format(self.__unknown_keys()))
        if not click.confirm('Delete these keys?'):
            sys.exit('Deletion of key aborted')

    def __authorized_keys_path(user):
        return os.path.join(os.sep, 'etc', 'ssh', 'users', user)


class CLI:
    """Commands to manage LDAP user SSH keys."""

    @click.group()
    @click.pass_obj
    def key(config):
        """Manage LDAP user SSH public keys."""
        pass

    @key.command()
    @click.option(
        '--username',
        '-u',
        required=True,
        help="Specify username to add key to")
    @click.option('--filename', '-f', help='File to load keys from')
    @click.pass_obj
    def add(config, username, filename):
        """Add user's SSH public key to their LDAP entry."""
        try:
            client = Client()
            client.prepare_connection()
            user_api = UserApi(client)
            key_api = API(client)
            key_api.add(username, user_api, filename)
        except (ldap3.core.exceptions.LDAPNoSuchAttributeResult,
                ldap_tools.exceptions.InvalidResult,
                ldap3.core.exceptions.LDAPAttributeOrValueExistsResult
                ) as err:  # pragma: no cover
            print('{}: {}'.format(type(err), err.args[0]))
        except Exception as err:  # pragma: no cover
            raise err from None

    @key.command()
    @click.option(
        '--username',
        '-u',
        required=True,
        help="Specify username to add key to")
    @click.option('--filename', '-f', help='File to load keys from')
    @click.option('--force', help='Force delete', is_flag=True)
    @click.pass_obj
    def remove(config, username, filename, force):
        """Remove user's SSH public key from their LDAP entry."""
        client = Client()
        client.prepare_connection()
        user_api = UserApi(client)
        key_api = API(client)
        key_api.remove(username, user_api, filename, force)

    @key.command()
    @click.pass_obj
    def install(config):  # pragma: no cover
        """Install user's SSH public key to the local system."""
        client = Client()
        client.prepare_connection()
        key_api = API(client)
        key_api.install()

    @key.command()
    @click.pass_obj
    def list(config):  # pragma: no cover
        """List SSH public key(s) from LDAP."""
        client = Client()
        client.prepare_connection()
        key_api = API(client)
        for key, values in key_api.get_keys_from_ldap().items():
            print("{}: ".format(key))
            for value in [v.decode() for v in values]:
                print("\t - {}".format(value))
            # print("{}: {}".format(key, [v.decode() for v in value]))

    @key.command()
    @click.option(
        '--username',
        '-u',
        required=True,
        help="Specify username to fetch keys for")
    @click.pass_obj
    def show(config, username):  # pragma: no cover
        """Show a user's SSH public key from their LDAP entry."""
        client = Client()
        client.prepare_connection()
        key_api = API(client)
        for key, value in key_api.get_keys_from_ldap(username).items():
            print(value)
