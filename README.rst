LDAP Tools
==========

This LDAP tools gem is designed as a wrapper around `ldap3` to make
interacting with LDAP easier. No knowledge of LDIF required.


+ Requirements_
+ Installation_

  * `Installation from pypi`_
  * `Installation from source`_

+ Configuration_

  * ldap_info.yaml_
  * ldap.secret_

+ Commands_

  * ldaptools_

    - `Currently supported subcommands`_

Requirements
------------

Use `pyenv` to install python 3.5.3 (or 3.6.4)

The following items are installed automatically as part of the pip install:
- ldap3
- click
- sshpubkeys
- pyyaml

Installation
------------

Installation from pypi
~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install ldap-tools

Installation from source
~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install git+https://github.com/carta/ldap_tools#egg=ldap_tools

Configuration
-------------

There are two files used by this application. The default location is
`$HOME/.ldap`; however, this can be overridden using the `LDAP_CONFIG_DIR`
environment variable

ldap_info.yaml
~~~~~~~~~~~~~~

This config file provides basic information about your LDAP server
setup.

.. code:: yaml

    ---
    server: # LDAP server
    user_dn: # DN of user to interact with LDAP
    port: # LDAP port
    basedn: #LDAP Base DN
    mail_domain: # Domain to be used for user email addresses
    service_ou: # Organization Unit (OU) for service accounts
    group_ou: # Organization Unit (OU) for groups

Note: DN of a user is the unique name used to identify that user


ldap.secret
~~~~~~~~~~~

This is a base64-encoded file with the LDAP root password.

Commands
--------

ldaptools
~~~~~~~~~

This is the base command from which all other commands are launched

::

    Usage: ldaptools [OPTIONS] COMMAND [ARGS]...

    Enter the application here.

    Options:
      --help  Show this message and exit.

    Commands:
      audit    Display LDAP group membership by user, by...
      group    LDAP Group Management Commands.
      key      Manage LDAP user SSH public keys.
      user     LDAP User Management Commands.
      version  LDAP Group Management Commands.

Help is available for all subcommands in a similar fashion.

Currently supported subcommands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  user create
-  user delete
-  group create
-  group delete
-  group add_user
-  group remove_user
-  key add
-  key remove
-  key install
-  audit by_user
-  audit by_group
-  audit raw
