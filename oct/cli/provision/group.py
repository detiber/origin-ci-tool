# coding=utf-8
from __future__ import absolute_import, division, print_function

from click import group

from .duffy.group import duffy
from .local.group import local
from .remote.group import remote

_SHORT_HELP = 'Provision a virtual machine for continuous integration tasks.'


@group(
    short_help=_SHORT_HELP,
    help=_SHORT_HELP + '''

Virtual machine provisioning is supported for a range of operating
systems, virtualization providers, and image stages. The choice of
operating system and virtualization provider allows for flexibility,
but it is the intention that all combinations have parity, so the
choice should not impact your workload.

The choice of image stage determines how far along the sync, build
and install process your VM begins. The following stages are supported:

\b
 - bare: bare operating system
 - base: RPM dependencies installed and configured, repositories cloned
 - build: artifacts and binaries built from repositories
 - install: OpenShift cluster installed from artifacts

Your choice of stage is not final: it is always possible to use
this tool to 'upgrade' your stage by running sync and install jobs
yourself. Furthermore, an 'install' stage can be re-synced and then
have all of the repositories re-installed to update it.
''',
)
def provision():
    """
    Do nothing -- this group should never be called without a sub-command.
    """

    pass


provision.add_command(duffy)
provision.add_command(local)
provision.add_command(remote)
