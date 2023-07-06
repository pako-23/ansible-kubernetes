image = 'debian/bookworm64'
masters = 1
nodes = 1
memory = 2048
cpus = 2

ansible_groups = {
    'kubernetes_masters' => [],
    'kubernetes_nodes' => [],
    'kubernetes:children' => [
        'kubernetes_masters',
        'kubernetes_nodes'
    ]
}

(1..masters).each { |i| ansible_groups['kubernetes_masters'].append "master-#{i}" }
(1..nodes).each { |i| ansible_groups['kubernetes_nodes'].append "node-#{i}" }

Vagrant.configure('2') do |config|
    config.ssh.insert_key = false

    config.vm.provider 'libvirt' do |v|
        v.qemu_use_session = false
        v.memory = memory
        v.cpus = cpus
    end

    config.vm.provider 'virtualbox' do |v|
        v.memory = memory
        v.cpus = cpus
    end

    nodes = ansible_groups['kubernetes_masters'] + ansible_groups['kubernetes_nodes']
    N = nodes.length-1

    (0..N).each do |i|
        config.vm.define nodes[i] do |node|
            node.vm.box = image
            node.vm.hostname = nodes[i]

            if i == N
                node.vm.provision :ansible do |ansible|
                    ansible.playbook = 'kubernetes.yaml'
                    ansible.limit = 'all'
                    ansible.groups = ansible_groups
                end
            end
        end
    end
end

