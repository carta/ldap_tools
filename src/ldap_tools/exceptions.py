"""Exception Classes."""


class ArgumentError(Exception):
    """Invalid command-line argument."""


class InvalidResult(Exception):
    """Invalid LDAP results."""


class NoGroupsFound(InvalidResult):
    """No groups returned by LDAP."""


class TooManyResults(InvalidResult):
    """Too many results returned by LDAP."""


class NoUserFound(InvalidResult):
    """No users returned by LDAP."""
