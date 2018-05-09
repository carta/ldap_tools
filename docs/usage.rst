=====
Usage
=====

To use `ldap_tools` in a project::

	import ldap_tools

CLI Examples
------------

user create
~~~~~~~~~~~
`ldaptools user create -n test user -g users`

user delete
~~~~~~~~~~~
`ldaptools user delete -u test.user`

group create
~~~~~~~~~~~~
`ldaptools group create -g test_group`

group delete
~~~~~~~~~~~~
`ldaptools group delete -g test_group`

group add_user
~~~~~~~~~~~~~~
`ldaptools group add_user -u test.user -g test_group`

group remove_user
~~~~~~~~~~~~~~~~~
`ldaptools group remove_user -u test.user -g test_group`

key add
~~~~~~~
`ldaptools key add -u test.user -f keyfile`

key remove
~~~~~~~~~~
`ldaptools key remove -u test.user -f keyfile`

key install
~~~~~~~~~~~
`ldaptools key install`

audit by_user
~~~~~~~~~~~~~
`ldaptools audit by_user`

audit by_group
~~~~~~~~~~~~~~
`ldaptools audit by_group`

audit raw
~~~~~~~~~
`ldaptools audit raw`