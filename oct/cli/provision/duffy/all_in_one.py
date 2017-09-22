# coding=utf-8
from __future__ import absolute_import, division, print_function

from click import Choice, UsageError, command, echo, option, pass_context
from cicoclient.wrapper import CicoWrapper


_SHORT_HELP = 'Provision a Duffy host for an All-In-One deployment.'


@command(
    name='all-in-one',
    short_help=_SHORT_HELP,
    help=_SHORT_HELP + '''

An All-In-One deployment of OpenShift uses one host on which
all cluster components are provisioned. These types of deployments are
most useful for short-term development work-flows.

\b
Examples:
  Provision a Duffy host with default parameters (centos, libvirt, bare)
  $ oct provision local all-in-one
\b
  Provision a Duffy host with custom parameters
  $ oct provision local all-in-one --os=centos --stage=bare
''',
)
@option(
    '--os',
    '-o',
    'operating_system',
    type=Choice([
        'centos'
    ]),
    default='centos',
    show_default=True,
    metavar='NAME',
    help='Host operating system.',
)
@option(
    '--arch',
    '-a',
    type=Choice([
        'x86_64',
        'aarch64',
        'ppc64le'
    ]),
    default='x86_64',
    show_default=True,
    metavar='NAME',
    help='Host architecture.',
)
@option(
    '--flavor',
    '-f',
    type=Choice([
        'tiny',
        'small',
        'medium',
        'lram.tiny',
        'lram.small',
        'xram.tiny',
        'xram.small',
        'xram.medium',
        'xram.large',
    ]),
    default='xram.medium',
    show_default=True,
    metavar='NAME',
    help='Host flavor (ignored for x86_64 hosts).',
)
@option(
    '--stage',
    '-s',
    type=Choice([
        'bare',
    ]),
    default='bare',
    show_default=True,
    metavar='NAME',
    help='Host image stage.',
)
@pass_context
def all_in_one_command(context, operating_system, arch, flavor, stage):
    """
    Provision a duffy host for an All-In-One deployment.

    :param context: Click context
    :param operating_system: host operating system
    :param arch: host architecture
    :param flavor: host flavor
    :param stage: image stage to base the host off of
    """
    configuration = context.obj
    configuration.run_playbook(
        playbook_relative_path='provision/duffy-up',
        playbook_variables={
            'origin_ci_duffy_arch': arch,
            'origin_ci_duffy_flavor': flavor,
            'origin_ci_duffy_groups': ['etcd', 'masters', 'nodes'],
            'origin_ci_inventory_dir': configuration.ansible_client_configuration.host_list,
            'openshift_schedulable': True,
            'openshift_node_labels': {
                'region': 'infra',
                'zone': 'default'
            }
        }
    )
