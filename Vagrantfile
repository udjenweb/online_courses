# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "Knowy/Ubuntu-14.04-Amd64"

  # Create a forwarded port mapping
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # docker-compose
  # config.vm.network 'forwarded_port', guest: 2376, host: 2376
  # server and db:
  config.vm.network 'forwarded_port', guest: 5000, host: 5000
  config.vm.network 'forwarded_port', guest: 5032, host: 5032


  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  config.vm.hostname = "eve.server.local"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # project dir
  config.vm.synced_folder ".", "/home/vagrant/online_courses",
    owner: 'vagrant',
    group: 'vagrant',
    mount_options: ["dmode=777", "fmode=777"]



  # Provider-specific configuration
  config.vm.provider "virtualbox" do |vb|
	 # Customize the amount of memory on the VM:
	 vb.memory = "1536"
  end

  # Enable provisioning with a shell script.
      config.vm.provision "shell", inline: <<-SHELL
        sudo echo "nameserver 8.8.8.8" >> /etc/resolv.conf
        sudo echo "nameserver 8.8.8.8" >> /etc/resolvconf/resolv.conf.d/base

        sudo apt-get update
        DEBIAN_FRONTEND=noninteractive sudo apt-get -y dist-upgrade

        sudo apt-get -y install python-pip
        sudo pip install unipath fabric fabtools

        sudo echo 'DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4 -H tcp://0.0.0.0:2376 -H unix:///var/run/docker.sock"' >> /etc/default/docker
        sudo service docker restart
      SHELL
      config.vm.provision "shell",
            inline: 'sudo service docker restart && cd /home/vagrant/online_courses && docker-compose up',
            run: "always"
end

