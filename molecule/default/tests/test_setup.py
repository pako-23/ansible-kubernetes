import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("kubernetes")


@pytest.mark.parametrize("module", ["overlay", "br_netfilter"])
def test_kernel_modules(host, module):
    result = host.run(f"lsmod | grep -wq '{module}'")
    assert result.rc == 0
    assert len(result.stderr) == 0


@pytest.mark.parametrize(
    "name,value",
    [
        ("net.bridge.bridge-nf-call-iptables", 1),
        ("net.bridge.bridge-nf-call-ip6tables", 1),
        ("net.ipv4.ip_forward", 1),
    ],
)
def test_networking_sysctl_values(host, name, value):
    assert host.sysctl(name) == value
