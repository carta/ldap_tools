"""LDAP Group Management API."""
import sys

import click
import ldap3

import ldap_tools.exceptions
from ldap_tools.client import Client


class API:
    """Methods to handle LDAP Group Management."""

    def __init__(self, client):
        """Initialize GROUP API and LDAP Client."""
        self.client = client

    def create(self, group, grouptype):
        """
        Create an LDAP Group.

        Raises:
            ldap3.core.exceptions.LDAPNoSuchObjectResult:
                an object involved with the request is missing

            ldap3.core.exceptions.LDAPEntryAlreadyExistsResult:
                the entity being created already exists

        """
        try:
            self.client.add(
                self.__distinguished_name(group), API.__object_class(),
                self.__ldap_attr(group, grouptype))
        except ldap3.core.exceptions.LDAPNoSuchObjectResult:  # pragma: no cover
            print(
                "Error creating LDAP Group.\nRequest: ",
                self.__ldap_attr(group, grouptype),
                "\nDistinguished Name: ",
                self.__distinguished_name(group),
                file=sys.stderr)
        except ldap3.core.exceptions.LDAPEntryAlreadyExistsResult:  # pragma: no cover
            print(
                "Error creating LDAP Group. Group already exists. \nRequest: ",
                self.__ldap_attr(group, grouptype),
                "\nDistinguished Name: ",
                self.__distinguished_name(group),
                file=sys.stderr)

    def delete(self, group):
        """Delete an LDAP Group."""
        self.client.delete(self.__distinguished_name(group))

    def add_user(self, group, username):
        """
        Add a user to the specified LDAP group.

        Args:
            group: Name of group to update
            username: Username of user to add

        Raises:
            ldap_tools.exceptions.InvalidResult:
                Results of the query were invalid.  The actual exception raised
                inherits from InvalidResult.  See #lookup_id for more info.

        """
        try:
            self.lookup_id(group)
        except ldap_tools.exceptions.InvalidResult as err:  # pragma: no cover
            raise err from None

        operation = {'memberUid': [(ldap3.MODIFY_ADD, [username])]}
        self.client.modify(self.__distinguished_name(group), operation)

    def remove_user(self, group, username):
        """
        Remove a user from the specified LDAP group.

        Args:
            group: Name of group to update
            username: Username of user to remove

        Raises:
            ldap_tools.exceptions.InvalidResult:
                Results of the query were invalid.  The actual exception raised
                inherits from InvalidResult.  See #lookup_id for more info.

        """
        try:
            self.lookup_id(group)
        except ldap_tools.exceptions.InvalidResult as err:  # pragma: no cover
            raise err from None

        operation = {'memberUid': [(ldap3.MODIFY_DELETE, [username])]}
        self.client.modify(self.__distinguished_name(group), operation)

    def index(self):
        """Return group info in a raw format."""
        return self.client.search(["(objectclass=posixGroup)"])

    def lookup_id(self, group):
        """
        Lookup GID for the given group.

        Args:
            group: Name of group whose ID needs to be looked up

        Returns:
            A bytestring representation of the group ID (gid)
            for the group specified

        Raises:
            ldap_tools.exceptions.NoGroupsFound:
                No Groups were returned by LDAP

            ldap_tools.exceptions.TooManyResults:
                More than one group was returned by LDAP

        """
        filter = ["(cn={})".format(group), "(objectclass=posixGroup)"]
        results = self.client.search(filter, ['gidNumber'])

        if len(results) < 1:
            raise ldap_tools.exceptions.NoGroupsFound(
                'No Groups Returned by LDAP')
        elif len(results) > 1:
            raise ldap_tools.exceptions.TooManyResults(
                'Multiple groups found. Please narrow your search.')
        else:
            return results[0].gidNumber.value

    def __distinguished_name(self, group):
        return "cn={},ou=Group,{}".format(group, self.client.basedn)

    def __ldap_attr(self, group, grouptype):
        attributes = {}
        attributes['cn'] = str.encode(group)
        attributes['gidnumber'] = self.client.get_max_id('group', grouptype)

        return attributes

    def __object_class():
        return ['top', 'posixGroup']


class CLI:
    """Commands to handle LDAP Group operations."""

    @click.group()
    @click.pass_obj
    def group(config):
        """LDAP Group Management Commands."""
        pass

    @group.command()
    @click.option(
        '--group', '-g', required=True, help="Specify group to create")
    @click.option(
        '--type',
        '-t',
        help='Specfy if this is a user or service group',
        default='user',
        show_default=True)
    @click.pass_obj
    def create(config, group, type):
        """Create an LDAP group."""
        if type not in ('user', 'service'):
            raise click.BadOptionUsage(  # pragma: no cover
                "--grouptype must be 'user' or 'service'")

        client = Client()
        client.prepare_connection()
        group_api = API(client)
        group_api.create(group, type)

    @group.command()
    @click.option('--group', '-g', required=True, help='Specify group')
    @click.option('--force', is_flag=True, help='Force delete')
    @click.pass_obj
    def delete(config, group, force):
        """Delete an LDAP group."""
        if not force:
            if not click.confirm(
                    'Confirm that you want to delete group {}'.format(group)):
                sys.exit("Deletion of {} aborted".format(group))

        client = Client()
        client.prepare_connection()
        group_api = API(client)
        group_api.delete(group)

    @group.command()
    @click.option(
        '--group', '-g', required=True, help='Specify group to add user to')
    @click.option(
        '--username',
        '-u',
        required=True,
        help='Specify username to add to group')
    @click.pass_obj
    def add_user(config, group, username):
        """Add specified user to specified group."""
        client = Client()
        client.prepare_connection()
        group_api = API(client)
        try:
            group_api.add_user(group, username)
        except ldap_tools.exceptions.NoGroupsFound:  # pragma: no cover
            print("Group ({}) not found".format(group))
        except ldap_tools.exceptions.TooManyResults:  # pragma: no cover
            print("Query for group ({}) returned multiple results.".format(
                group))
        except ldap3.TYPE_OR_VALUE_EXISTS:  # pragma: no cover
            print("{} already exists in {}".format(username, group))

    @group.command()
    @click.option(
        '--group',
        '-g',
        required=True,
        help='Specify group to remove user from')
    @click.option(
        '--username',
        '-u',
        required=True,
        help='Specify username to remove from group')
    @click.pass_obj
    def remove_user(config, group, username):
        """Remove specified user from specified group."""
        client = Client()
        client.prepare_connection()
        group_api = API(client)
        try:
            group_api.remove_user(group, username)
        except ldap_tools.exceptions.NoGroupsFound:  # pragma: no cover
            print("Group ({}) not found".format(group))
        except ldap_tools.exceptions.TooManyResults:  # pragma: no cover
            print("Query for group ({}) returned multiple results.".format(
                group))
        except ldap3.NO_SUCH_ATTRIBUTE:  # pragma: no cover
            print("{} does not exist in {}".format(username, group))

    @group.command()
    @click.pass_obj
    def index(config):  # pragma: no cover
        """Display group info in raw format."""
        client = Client()
        client.prepare_connection()
        group_api = API(client)
        print(group_api.index())
