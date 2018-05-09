"""LDAP User Management API."""
import os
import string
import sys
from base64 import b64encode
from hashlib import sha1
from random import SystemRandom

import click

import ldap_tools.exceptions
from ldap_tools.client import Client
from ldap_tools.group import API as GroupApi


class API:
    """Methods to handle LDAP Group Management."""

    def __init__(self, client):
        """Initialize User API and LDAP Client."""
        # TODO: pass the client in instead of instantiating here
        self.client = client

    def create(self, fname, lname, group, type, group_api):
        """Create an LDAP User."""
        self.__username(fname, lname)
        self.client.add(
            self.__distinguished_name(type, fname=fname, lname=lname),
            API.__object_class(),
            self.__ldap_attr(fname, lname, type, group, group_api))

    def delete(self, username, type):
        """Delete an LDAP user."""
        self.client.delete(self.__distinguished_name(type, username=username))

    def index(self):
        """Return user info in LDIF format."""
        filter = ["(objectclass=posixAccount)"]
        return self.client.search(filter)

    def show(self, username):
        """Return a specific user's info in LDIF format."""
        filter = ['(objectclass=posixAccount)', "(uid={})".format(username)]
        return self.client.search(filter)

    def find(self, username):
        """
        Find user with given username.

        Args:
            username Username of the user to search for

        Raises:
            ldap_tools.exceptions.NoUserFound: No users returned by LDAP
            ldap_tools.exceptions.TooManyResults:
                Multiple users returned by LDAP

        """
        filter = ['(uid={})'.format(username)]
        results = self.client.search(filter)

        if len(results) < 1:
            raise ldap_tools.exceptions.NoUserFound(
                'User ({}) not found'.format(username))
            return  # pragma: no cover
        elif len(results) > 1:
            raise ldap_tools.exceptions.TooManyResults(
                'Multiple users found. Please narrow your search.')
            return  # pragma: no cover
        else:
            return results

    def __username(self, fname, lname):  # pragma: no cover
        """Convert first name + last name into first.last style username."""
        self.username = '.'.join([i.lower() for i in [fname, lname]])

    def __distinguished_name(self, type, fname=None, lname=None,
                             username=None):  # pragma: no cover
        """Assemble the DN of the user."""
        if username is None:
            uid = "uid={}".format(self.username)
        else:
            uid = "uid={}".format(username)

        dn_list = [
            uid,
            "ou={}".format(self.__organizational_unit(type)),
            self.client.basedn,
        ]

        return ','.join(dn_list)

    def __ldap_attr(self, fname, lname, type, group,
                    group_api):  # pragma: no cover
        """User LDAP attributes."""
        return {
            'uid':
            str(self.username).encode(),
            'cn':
            ' '.join([fname, lname]).encode(),
            'sn':
            str(lname).encode(),
            'givenname':
            str(fname).encode(),
            'homedirectory':
            os.path.join(os.path.sep, 'home', self.username).encode(),
            'loginshell':
            os.path.join(os.path.sep, 'bin', 'bash').encode(),
            'mail':
            '@'.join([self.username, self.client.mail_domain]).encode(),
            'uidnumber':
            self.__uidnumber(type),
            'gidnumber':
            API.__gidnumber(group, group_api),
            'userpassword':
            str('{SSHA}' + API.__create_password().decode()).encode(),
        }

    def __organizational_unit(self, type):  # pragma: no cover
        if type == 'user':
            return 'People'
        elif type == 'service':
            return self.client.service_ou
        else:
            print('Unknown type: {}'.format(type), file=sys.stderr)

    def __gidnumber(group, group_api):  # pragma: no cover
        """Get first usable GID."""
        return group_api.lookup_id(group)

    def __uidnumber(self, type):  # pragma: no cover
        """Get first usable UID."""
        return self.client.get_max_id('user', type)

    def __create_password():  # pragma: no cover
        """Create a password for the user."""
        salt = b64encode(API.__generate_string(32))
        password = b64encode(API.__generate_string(64))
        return b64encode(sha1(password + salt).digest())

    def __generate_string(length):  # pragma: no cover
        """Generate a string for password creation."""
        return ''.join(
            SystemRandom().choice(string.ascii_letters + string.digits)
            for x in range(length)).encode()

    def __object_class():  # pragma: no cover
        return [
            'top', 'posixAccount', 'shadowAccount', 'inetOrgPerson',
            'organizationalPerson', 'person', 'ldapPublicKey'
        ]


class CLI:
    """Commandline for User commands."""

    def show_user(listing):  # pragma: no cover
        """Show users for index or show commandline parameters."""
        for user in listing:
            print(user)

    @click.group()
    @click.pass_obj
    def user(config):
        """LDAP User Management Commands."""
        pass

    @user.command()
    @click.option(
        '--name',
        '-n',
        required=True,
        help="Specify user's first and last name",
        nargs=2)
    @click.option(
        '--group', '-g', required=True, help='Specify name of primary group')
    @click.option(
        '--type',
        '-t',
        help='Specfy if this is a user or service account',
        default='user',
        show_default=True)
    @click.pass_obj
    def create(config, name, group, type):
        """Create an LDAP user."""
        if type not in ('user', 'service'):
            raise click.BadOptionUsage("--type must be 'user' or 'service'")
        client = Client()
        client.prepare_connection()
        user_api = API(client)
        group_api = GroupApi(client)
        user_api.create(name[0], name[1], group, type, group_api)

    @user.command()
    @click.option(
        '--username', '-u', required=True, help="Specify username to delete")
    @click.option(
        '--type',
        '-t',
        help='Specfy if this is a user or service account',
        default='user',
        show_default=True)
    @click.pass_obj
    def delete(config, username, type):
        """Delete an LDAP user."""
        client = Client()
        client.prepare_connection()
        user_api = API(client)
        user_api.delete(username, type)

    @user.command()
    @click.pass_obj
    def index(config):
        """Display user info in LDIF format."""
        client = Client()
        client.prepare_connection()
        user_api = API(client)
        CLI.show_user(user_api.index())

    @user.command()
    @click.option(
        '--username', '-u', required=True, help="Specify username to delete")
    @click.pass_obj
    def show(config, username):
        """Display a specific user."""
        client = Client()
        client.prepare_connection()
        user_api = API(client)
        CLI.show_user(user_api.show(username))
