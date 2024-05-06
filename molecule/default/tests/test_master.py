import json
import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("kubernetes_masters")


@pytest.mark.parametrize(
    "path",
    [
        "/etc/kubernetes/admin.conf",
        "/etc/kubernetes/controller-manager.conf",
        "/etc/kubernetes/kubeadm-config.yaml",
        "/etc/kubernetes/scheduler.conf",
        "/root/.kube/config",
    ],
)
def test_kubelet_config(host, path):
    config_file = host.file(path)
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == "root"
    assert config_file.group == "root"
    assert config_file.mode == 0o600
    assert len(config_file.content) > 0
    assert config_file.content_string[-1] == "\n"


def test_kubectl_nodes(host):
    nodes = set(
        testinfra.utils.ansible_runner.AnsibleRunner(
            os.environ["MOLECULE_INVENTORY_FILE"]
        ).get_hosts("kubernetes")
    )
    result = host.run("kubectl get nodes --output=json")
    assert result.rc == 0
    registered_nodes = json.loads(result.stdout)["items"]
    assert nodes == set([node["metadata"]["name"] for node in registered_nodes])


def test_kubectl_create_pod(host):
    name = host.ansible.get_variables()["inventory_hostname"]
    assert host.run(f"kubectl run --image=nginx '{name}-kubectl'").rc == 0
    assert host.run(f"kubectl delete pod '{name}-kubectl'").rc == 0


def test_ansible_create_pod(host):
    name = host.ansible.get_variables()["inventory_hostname"]
    definition = {
        "definition": {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": name, "namespace": "default"},
            "spec": {"containers": [{"image": "nginx", "name": "test"}]},
        }
    }

    assert "result" in host.ansible(
        "kubernetes.core.k8s",
        "definition={{ definition }}",
        extra_vars=definition,
        become=True,
    )
    assert "result" in host.ansible(
        "kubernetes.core.k8s",
        "definition={{ definition }} state=absent",
        extra_vars=definition,
        become=True,
    )
