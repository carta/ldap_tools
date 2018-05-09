"""Command line application entry point."""
import click  # pragma: no cover

import ldap_tools  # pragma: no cover
from ldap_tools.audit import CLI as AuditCLI  # pragma: no cover
from ldap_tools.group import CLI as GroupCLI  # pragma: no cover
from ldap_tools.key import CLI as KeyCLI  # pragma: no cover
from ldap_tools.user import CLI as UserCLI  # pragma: no cover


class CLI:  # pragma: no cover
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.invoked_subcommand

    @cli.command()
    def version():
        """LDAP Group Management Commands."""
        print(ldap_tools.__version__)


@click.group()  # pragma: no cover
def entry_point():  # pragma: no cover
    """Enter the application here."""
    pass


def main():  # pragma: no cover
    """Enter main function."""
    entry_point.add_command(CLI.version)
    entry_point.add_command(UserCLI.user)
    entry_point.add_command(GroupCLI.group)
    entry_point.add_command(AuditCLI.audit)
    entry_point.add_command(KeyCLI.key)

    entry_point()
