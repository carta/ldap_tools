"""Audit LDAP Permissions."""
import click

from ldap_tools.client import Client


class API:
    """Methods to handle LDAP Auditing."""

    def __init__(self, client):
        self.client = client

    def by_user(self):  # pragma: no cover
        """
        Display group membership sorted by group.

        Returns:
            Array with a dictionary of group membership.
                For example: {'test.user': ['testgroup', 'testgroup2']}

        """
        users = [i for i in self.__get_users()]
        user_groups = {}
        group_results = {
            tuple(value): key
            for (key, value) in self.by_group().items()
        }
        for user in users:
            user_groups[user] = []
            for user_list, group in group_results.items():
                if user in user_list:
                    user_groups[user].append(group)

        return user_groups

    def by_group(self):  # pragma: no cover
        """
        Display group membership sorted by group.

        Returns:
            Array with a dictionary of group membership.
                For example: {'testgroup': ['test.user', 'test.user2']}

        """
        group_membership = {}
        for record in self.__get_groups_with_membership():
            group_membership[record.cn.value] = [
                i for i in record.memberUid.values
            ]
        return group_membership

    def raw(self):  # pragma: no cover
        """Dump contents of LDAP directory to console."""
        return self.client.search(None)

    def __get_groups_with_membership(self):  # pragma: no cover
        """Get group membership."""
        filter = ['(objectclass=posixGroup)', '(memberuid=*)']
        results = self.client.search(filter, ['cn', 'memberUid'])

        return results

    def __get_users(self):  # pragma: no cover
        """Get user list."""
        filter = ['(objectclass=posixAccount)']
        results = self.client.search(filter, ['uid'])
        for result in results:
            yield result.uid.value


class CLI:
    """Commands to audit LDAP permissions."""

    @click.group()
    @click.pass_obj
    def audit(config):
        """Display LDAP group membership by user, by group, or in raw format."""
        pass

    @audit.command()
    @click.pass_obj
    def by_user(config):
        """Display LDAP group membership sorted by user."""
        client = Client()
        client.prepare_connection()
        audit_api = API(client)
        CLI.parse_membership('Groups by User', audit_api.by_user())

    @audit.command()
    @click.pass_obj
    def by_group(config):
        """Display LDAP group membership sorted by group."""
        client = Client()
        client.prepare_connection()
        audit_api = API(client)
        CLI.parse_membership('Users by Group', audit_api.by_group())

    @audit.command()
    @click.pass_obj
    def raw(config):  # pragma: no cover
        """Dump the contents of LDAP to console in raw format."""
        client = Client()
        client.prepare_connection()
        audit_api = API(client)
        print(audit_api.raw())

    def parse_membership(header_string, membership):  # pragma: no cover
        """Print membership for #by_group and #by_user."""
        print(header_string, "\n{}".format('=' * len(header_string)))
        for key, values in membership.items():
            if values is None:
                continue
            print('- ', key)
            for value in values:
                print("\t- {}".format(value))
