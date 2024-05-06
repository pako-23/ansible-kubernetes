import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("kubernetes")


@pytest.mark.parametrize("package", ["kubelet", "kubeadm", "kubectl"])
def test_kubernetes_packages(host, package):
    variables = host.ansible.get_variables()
    assert "kubernetes_version" in variables
    assert host.package(package).is_installed
    assert host.package(package).version.startswith(variables["kubernetes_version"])
    assert host.find_command(package)


def test_kubelet_started(host):
    service = host.service("kubelet")
    assert service.is_enabled
    assert service.is_running


@pytest.mark.parametrize(
    "path,permission",
    [("/var/lib/kubelet/config.yaml", 0o644), ("/etc/kubernetes/kubelet.conf", 0o600)],
)
def test_kubelet_config(host, path, permission):
    config_file = host.file(path)
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == "root"
    assert config_file.group == "root"
    assert config_file.mode == permission
    assert len(config_file.content) > 0
    assert config_file.content_string[-1] == "\n"
