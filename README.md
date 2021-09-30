<p><h1>RPi A-Z Configuration</h1><p>

<p><h2>RPi Firmware update</h1><p>

OPTION 1:
 ```javascript
sudo apt update &&
sudo apt full-upgrade
```

 HEADER 1: aaa
 
Now restart Raspberry Pi using:

 ```javascript 
sudo shutdown - r now
 ```
  
  Check firmware version with :
  ```javascript
  sudo rpi-eeprom-update
   ```
    
    OPTION 2:
```javascript 
<p>sudo apt update && sudo apt upgrade -y<p>
 sudo apt install rpi-eeprom rpi-eeprom-images
```    
    Instalar rpi-eeprom:  sudo apt install rpi-eeprom rpi-eeprom-images
Actualizar Firmware: sudo rpi-eeprom-update -a

<h2>Schedule Crontab for checking and installing updates daily/once its rebooted</h1>

 Open crontab:
 ```
crontab -e
```
Update it every midnight and every restart:
```
0 0 * * * sudo apt update && sudo apt upgrade
@reboot sudo apt update && sudo apt upgrade
```
If your script isn't executing, check the system log for cron events:
grep cron /var/log/syslog

If you wish to view your scheduled tasks without editing you can use the command:
crontab -l 

<p><h1>RPi Projects</h1><p>

<h2>TailScale VPN setup</h2>

```
sudo apt-get install apt-transport-https &&
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add - &&
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list &&
sudo apt-get update &&
sudo apt-get install tailscale &&
sudo tailscale up &&
tailscale ip -4 #get the ip 

#sudo tailscale logout
#sudo tailscale down
 ```
 
#To force all the traffic to go through the Rpi, Port forwarding is needed:

```
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf &&
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf &&
sudo sysctl -p /etc/sysctl.conf &&
sudo tailscale down
```

With this final command, the Rpi will be an exit node:

```
sudo tailscale up --advertise-exit-node
```
 
 <h2>Install GIT and sync your repos</h2>
 
 ```
 sudo apt install git &&
 git clone https://github.com/reisikei/RPi.git &&
 cd RPi &&
 git pull #to make sure its up to date (a cron task could be scheduled)
```
