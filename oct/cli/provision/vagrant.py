import click
import config
from cli.util.common_options import ansible_verbosity_option, ansible_dry_run_option, ansible_debug_mode_option
from config.load import safe_update_config
from util.playbook_runner import PlaybookRunner
from util.playbook import playbook_path


class OperatingSystem:
    """
    An enumeration of supported operating systems for
    Vagrant provisioning of local VMs.
    """
    fedora = 'fedora'
    centos = 'centos'


class Provider:
    """
    An enumeration of supported Vagrant providers for
    provisioning of local VMs.
    """
    libvirt = 'libvirt'
    virtualbox = 'virtualbox'
    vmware = 'vmware'


class Stage:
    """
    An enumeration of supported stages for boxes used
    for Vagrant provisioning of local VMs.
    """
    bare = 'bare'
    base = 'base'
    install = 'install'


def destroy_callback(ctx, param, value):
    """
    Tear down the currently running VM using `vagrant destroy`

    :param value: whether or not to tear down the VM
    """
    if not value or ctx.resilient_parsing:
        return

    destroy()
    ctx.exit()


@click.command(
    short_help='Bring up a local VM using Vagrant.',
    help='''
Provisions a local VM using Vagrant.

Local VM provisioning is supported for a range of operating systems,
Vagrant providers, and image stages. The choice of operating system
and Vagrant provider allows for flexibility, but it is the intention
that all combinations have parity, so the choice should not impact
your workload.

The choice of image stage determines how far long the sync, build
and install process your VM begins. The following stages are supported:

\b
 - bare: bare operating system
 - base: RPM dependencies installed and configured, repositories cloned
 - install: artifacts and binaries built and installed from repositories

Your choice of stage is not final: it is always possible to use
this tool to 'upgrade' your stage by running sync and install jobs
yourself. Furthermore, an 'install' stage can be re-synced and then
have all of the repositories re-installed to update it.

Note: without a license to publish and distribute VMWare Fusion box
files, we cannot provide any image stage other than the most basic
bare operating system stage. If you are using VMWare Fusion as your
Vagrant provider, you must build the other image stages yourself.

\b
Examples:
  Provision a VM with default parameters (fedora, libvirt, install)
  $ oct provision vagrant
\b
  Provision a VM with custom parameters
  $ oct provision vagrant --os=centos --provider=virtualbox --stage=base
\b
  Tear down the currently running VM
  $ oct provision vagrant --destroy
\b
  Provision a VM with a specific IP address
  $ oct provision vagrant --ip=10.245.2.2
'''
)
@click.option(
    '--os', '-o',
    'operating_system',
    type=click.Choice([
        OperatingSystem.fedora,
        OperatingSystem.centos
    ]),
    default=OperatingSystem.fedora,
    show_default=True,
    help='VM operating system.'
)
@click.option(
    '--provider', '-p',
    type=click.Choice([
        Provider.libvirt,
        Provider.virtualbox,
        Provider.vmware
    ]),
    default=Provider.libvirt,
    show_default=True,
    help='Virtualization provider.'
)
@click.option(
    '--stage', '-s',
    type=click.Choice([
        Stage.bare,
        Stage.base,
        Stage.install
    ]),
    default=Stage.install,
    show_default=True,
    help='VM image stage.'
)
@click.option(
    '--master-ip', '-i',
    'ip',
    default='10.245.2.2',
    show_default=True,
    help='Desired IP of the VM.'
)
@click.option( #TODO: why doesn't this work with verbosity, debug? seems like ordering of eager callbacks is right
    '--destroy', '-d',
    is_flag=True,
    expose_value=False,
    help='Tear down the current VM.',
    callback=destroy_callback,
    is_eager=True
)
@ansible_verbosity_option
@ansible_dry_run_option
@ansible_debug_mode_option
def vagrant(operating_system, provider, stage, ip):
    """
    Provision a local VM using Vagrant.

    :param operating_system: operating system to use for the VM
    :param provider: provider to use with Vagrant
    :param stage: image stage to base the VM off of
    :param ip: desired VM IP address
    """
    validate(provider, stage)
    provision(operating_system, provider, stage, ip)


def validate(provider, stage):
    """
    Validate that the stage requested exists for the provider.
    We do not have a license for posting or distributing any
    VMWare Fusion images, so we cannot provide any stage more
    advanced than the bare OS for this provider.

    :param provider: Vagrant provider chosen
    :param stage: image stage chosen
    """
    if provider == Provider.vmware and stage != Stage.bare:
        raise click.UsageError('Only the %s stage is supported for the %s provider.' % (Stage.bare, Provider.vmware))


def provision(operating_system, provider, stage, ip):
    """
    Provision a local VM using Vagrant.

    :param operating_system: operating system to use for the VM
    :param provider: provider to use with Vagrant
    :param stage: image stage to base the VM off of
    :param ip: desired VM IP address
    """
    PlaybookRunner().run(
        playbook_source=playbook_path('provision/vagrant-up'),
        vars=dict(
            origin_ci_vagrant_home_dir=config._vagrant_home,
            origin_ci_vagrant_os=operating_system,
            origin_ci_vagrant_provider=provider,
            origin_ci_vagrant_stage=stage,
            origin_ci_vagrant_ip=ip,
            origin_ci_vagrant_hostname=config._config['vm_hostname']
        )
    )

    # if we successfully executed the playbook, we have a new host
    config.add_host_to_inventory(config._config['vm_hostname'])
    config._config['vm'] = dict(
        operating_system=operating_system,
        provider=provider,
        stage=stage
    )
    safe_update_config()


def destroy():
    """
    Tear down the currently running Vagrant VM.
    """
    PlaybookRunner().run(
        playbook_source=playbook_path('provision/vagrant-down'),
        vars=dict(
            origin_ci_vagrant_home_dir=config._vagrant_home
        )
    )

    # if we successfully executed the playbook, we have removed a host
    config.remove_host_from_inventory(config._config['vm_hostname'])
    config._config.pop('vm')
    safe_update_config()
