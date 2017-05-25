# -*- mode: ruby -*-
# vi: set ft=ruby :

vmname = 'mikrotik-6-38-1'

# Specify minimum Vagrant version and Vagrant API version
Vagrant.require_version ">= 1.6.0"
VAGRANTFILE_API_VERSION = "2"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  #config.vm.box = 'mikrotik-6-38-1'
  config.vm.box = vmname
  config.vm.hostname = 'mikrotik01'
  config.vm.network "private_network", ip: '192.168.60.202'
  config.vm.network "private_network", ip: '192.168.60.203'
  config.vm.network "private_network", ip: '192.168.60.204'
  config.vm.network "private_network", ip: '192.168.60.205'
  config.vm.network "private_network", ip: '192.168.60.206'
  config.vm.network "private_network", ip: '192.168.60.207'
  config.vm.network "private_network", ip: '192.168.60.208'
  config.vm.network "private_network", ip: '192.168.60.209'
  config.vm.network "private_network", ip: '192.168.60.210'
  config.vm.network "private_network", ip: '192.168.60.211'
  config.vm.network "private_network", ip: '192.168.60.212'
  config.vm.network :forwarded_port, guest: 22, host: 2301, id: 'ssh'
  config.vm.network :forwarded_port, guest: 8728, host: 8728, id: 'api'
  config.vm.network :forwarded_port, guest: 80, host: 8080, id: 'web'

  config.vm.provider :virtualbox do |vb|
      vb.name = vmname + '_test'
  end
end
