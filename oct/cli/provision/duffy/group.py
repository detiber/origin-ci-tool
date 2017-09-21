# coding=utf-8
from __future__ import absolute_import, division, print_function

from click import group

from .all_in_one import all_in_one_command

_SHORT_HELP = 'Provision virtual machines under a duffy provisioned host.'


@group(
    short_help=_SHORT_HELP,
    help=_SHORT_HELP + '''

Duffy provisioning is supported for provisioning machines within the
ci.centos.org environment''',
)
def duffy():
    """
    Do nothing -- this group should never be called without a sub-command.
    """

    pass


duffy.add_command(all_in_one_command)
