"""LDAP Client Class."""
import base64
import os

import ldap3
import yaml

import ldap_tools.exceptions


class Client:
    """Methods to manage LDAP client."""

    def __init__(self):
        """Initialize Client class."""
        self.config_dir = Client.__ldap_config_directory()

    def prepare_connection(self):  # pragma: no cover
        """Prepare connection to LDAP client."""
        self.load_ldap_config()
        self.load_ldap_password()
        self.connection()

    def load_ldap_config(self):  # pragma: no cover
        """Configure LDAP Client settings."""
        try:
            with open('{}/ldap_info.yaml'.format(self.config_dir),
                      'r') as FILE:
                config = yaml.load(FILE)
                self.host = config['server']
                self.user_dn = config['user_dn']
                self.port = config['port']
                self.basedn = config['basedn']
                self.mail_domain = config['mail_domain']
                self.service_ou = config['service_ou']
        except OSError as err:
            print('{}: Config file ({}/ldap_info.yaml) not found'.format(
                type(err), self.config_dir))

    def load_ldap_password(self):  # pragma: no cover
        """Import LDAP password from file."""
        with open('{}/ldap.secret'.format(self.config_dir), 'r') as FILE:
            secure_config = FILE.read()
            self.user_pw = base64.b64decode(secure_config.encode())

    def connection(self):  # pragma: no cover
        """Establish LDAP connection."""
        # self.server allows us to fetch server info
        # (including LDAP schema list) if we wish to
        # add this feature later
        self.server = ldap3.Server(self.host, port=self.port, get_info=ldap3.ALL)
        self.conn = ldap3.Connection(
            self.server,
            user=self.user_dn,
            password=self.user_pw,
            auto_bind=True,
            lazy=True,
            receive_timeout=1)

    def add(self, distinguished_name, object_class, attributes):
        """
        Add object to LDAP.

        Args:
            distinguished_name: the DN of the LDAP record to be added
            object_class: The objectClass of the record to be added.
                This is a list of length >= 1.
            attributes: a dictionary of LDAP attributes to add
                See ldap_tools.api.group.API#__ldap_attr

        """
        self.conn.add(distinguished_name, object_class, attributes)

    def delete(self, distinguished_name):  # pragma: no cover
        """Remove object from LDAP."""
        return self.conn.delete(distinguished_name)

    def modify(self, distinguished_name, mod_list):  # pragma: no cover
        """
        Modify an object in LDAP.

        Args:
            distinguished_name: DN of object to modify
            mod_list: An LDAP hash with a list of tuples containing an operation,
                an attribute name, and a desired value for the attribute.
                For example:

                mod_list = {'memberUid': [(ldap3.MODIFY_ADD, [username])]}
        """

        self.conn.modify(distinguished_name, mod_list)

    def search(self, filter, attributes=None):
        """Search LDAP for records."""
        if attributes is None:
            attributes = ['*']

        if filter is None:
            filter = ["(objectclass=*)"]

        # Convert filter list into an LDAP-consumable format
        filterstr = "(&{})".format(''.join(filter))
        self.conn.search(
            search_base=self.basedn,
            search_filter=filterstr,
            search_scope=ldap3.SUBTREE,
            attributes=attributes)
        return self.conn.entries

    def get_max_id(self, object_type, role):
        """Get the highest used ID."""
        if object_type == 'user':
            objectclass = 'posixAccount'
            ldap_attr = 'uidNumber'
        elif object_type == 'group':  # pragma: no cover
            objectclass = 'posixGroup'
            ldap_attr = 'gidNumber'
        else:
            raise ldap_tools.exceptions.InvalidResult('Unknown object type')

        minID, maxID = Client.__set_id_boundary(role)

        filter = [
            "(objectclass={})".format(objectclass), "({}>={})".format(ldap_attr, minID)
        ]

        if maxID is not None:
            filter.append("({}<={})".format(ldap_attr, maxID))

        id_list = self.search(filter, [ldap_attr])

        if id_list == []:
            id = minID
        else:
            if object_type == 'user':
                id = max([i.uidNumber.value for i in id_list]) + 1
            elif object_type == 'group':
                id = max([i.gidNumber.value for i in id_list]) + 1
            else:
                raise ldap_tools.exceptions.InvalidResult('Unknown object')

        return id

    def __ldap_config_directory():
        return os.getenv('LDAP_CONFIG_DIR', "{}/.ldap".format(
            os.getenv('HOME')))

    def __set_id_boundary(role):
        if role == 'user':
            minID = 10000
            maxID = 19999
            return [minID, maxID]
        elif role == 'service':
            minID = 20000
            maxID = None
            return [minID, maxID]
        else:
            raise ldap_tools.exceptions.InvalidResult(
                'Unknown Role: {}'.format(role))
