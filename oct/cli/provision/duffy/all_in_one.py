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
    ssid = provision_with_duffy(arch, flavor)
#    register_host(configuration, ssid, operating_system, stage)


def provision_with_duffy(arch, flavor):
    """
    Provision a host using Duffy.

    :param arch: host architecture
    :param flavor: host flavor
    """
    cico = CicoWrapper(endpoint='http://admin.ci.centos.org:8080/')
    echo("Requesting host from Duffy")
    hosts, ssid = cico.node_get(arch=arch, flavor=flavor)
    echo("Duffy ssid: {}".format(ssid))
    echo("Duffy host: {}".format(hosts))
    return ssid


def register_host(configuration, ssid, operating_system, stage):
    """
    Register a new host by updating metadata records for the
    new host both in the in-memory cache for this process and
    the on-disk records that will persist past this CLI call.

    :param configuration: Origin CI tool configuration
    :param ssid: Duffy ssid
    :param operating_system: Host operating system
    :param stage: image stage the host was based off of
    """
    cico = CicoWrapper(endpoint='http://admin.ci.centos.org:8080/')
    inventory = cico.inventory(ssid=ssid)
    hostname, host_props = inventory.popitem()

    configuration.register_duffy_host(
        DuffyHostMetadata(
            data={
                'provisioning_details': {
                    'ssid': ssid,
                    'hostname': hostname,
                    'operating_system': operating_system,
                    'arch': host_props['architecture'],
                    'flavor': host_props['flavor'],
                    'stage': stage,
                },
                # we are supporting an all-in-one deployment with the
                # host, so this host will be both a master and a node
                'groups': [
                    'etcd',
                    'masters',
                    'nodes',
                ],
                # no `infra` region exists as we need the same node to
                # host OpenShift infrastructure and be schedule-able
                'extra': {
                    'openshift_schedulable': True,
                    'openshift_node_labels': {
                        'region': 'infra',
                        'zone': 'default',
                    },
                },
            }
        )
    )
