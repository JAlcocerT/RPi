# RPi<h1>RPi Firmware update</h1>

OPTION 1:
<p>sudo apt update<p>
<p>sudo apt full-upgrade<p>

<p>Now restart Raspberry Pi using:<p>

<p>sudo shutdown - r now<p>
  
  <p>Check firmware version:<p>
  <p>sudo rpi-eeprom-update<p>
   
    OPTION 2:
    <p>sudo apt update && sudo apt upgrade -y<p>
    sudo apt install rpi-eeprom rpi-eeprom-images
    
    Instalar rpi-eeprom:  sudo apt install rpi-eeprom rpi-eeprom-images
Actualizar Firmware: sudo rpi-eeprom-update -a

<h1>Schedule Crontab for checking and installing updates daily/once its rebooted</h1>

 open crontab:

crontab -e

If your script isn't executing, check the system log for cron events:

grep cron /var/log/syslog

If you wish to view your scheduled tasks without editing you can use the command:

crontab -l 



<h1>TailScale VPN setup</h1>

<p>sudo apt-get install apt-transport-https
<p>curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add -
<p>curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list
<p>sudo apt-get update
<p>sudo apt-get install tailscale
<p>sudo tailscale up
<p>tailscale ip -4 #get the ip

<p>#sudo tailscale logout
<p>#sudo tailscale down
  
<p>To force all the traffic to go through the Rpi, Port forwarding is needed:

<p>echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
<p>echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf
<p>sudo sysctl -p /etc/sysctl.conf

<p>sudo tailscale down

<p>With this final command, the Rpi will be an exit node:

<p>sudo tailscale up --advertise-exit-node
