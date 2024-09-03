---
title: "Others: "
date: 2023-08-30T23:20:21+01:00
draft: true
tags: ["Self-Hosting"]
---

## DRONE

* Haga un PEQUEÑO dron Arduino con cámara FPV: ¿volará?

https://www.youtube.com/watch?v=Sa6EslOHsI0

* Haga un avión de papel FPV RC que vuele | ESP32


https://www.youtube.com/watch?v=hDjBi0ErDdw

* Open Source Motion Capture for Autonomous Drones

https://www.youtube.com/watch?v=0ql20JKrscQ
https://github.com/jyjblrd/Low-Cost-Mocap
https://github.com/jyjblrd/Low-Cost-Mocap?tab=MIT-1-ov-file#readme
> Low cost motion capture system for room scale tracking



## RPi + LCD

https://www.youtube.com/watch?v=3XLjVChVgec

HOWTO Raspberry Pi + LCD 16x2 i2c



https://github.com/the-raspberry-pi-guy/lcd

## MPU6050


There are many 3-axis accelerometers that you can use with the Raspberry Pi Pico. Some of the most popular options include:

MPU-6050: This is a popular and versatile accelerometer that is also compatible with the Raspberry Pi Pico. It has a wide range of features, including a built-in gyroscope.


**biblioman09**

<https://www.youtube.com/watch?v=JXyHuZyqjxU>

## BME280 Sensor

Temp Hum and Preassure

I2C

<https://www.youtube.com/watch?v=GQOqvvei5Do>


### GCP

<https://cloud.google.com/free/docs/free-cloud-features#compute>


gcloud compute instances create instance-1 \
    --project=projectrpi-398008 \
    --zone=us-east1-b \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=267146020937-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name=instance-1,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230814,mode=rw,size=10,type=projects/projectrpi-398008/zones/us-central1-a/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any




## GCP Free Tier

<https://cloud.google.com/free>


### Pub/Sub

<https://cloud.google.com/free/docs/free-cloud-features#pub-sub>

<https://www.youtube.com/watch?v=jYIgcdIW1yk>



### Compute Engine


## AWS


### AWS IoT

<https://www.youtube.com/watch?v=hgQ-Ewrm48c>

## Terraform

#Este código es compatible con Terraform 4.25.0 y versiones compatibles con 4.25.0.
#Para obtener información sobre la validación de este código de Terraform, consulta https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

resource "google_compute_instance" "instance-1" {
  boot_disk {
    auto_delete = true
    device_name = "instance-1"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-11-bullseye-v20230814"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  machine_type = "e2-micro"
  name         = "instance-1"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    subnetwork = "projects/projectrpi-398008/regions/us-east1/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = "267146020937-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  zone = "us-east1-b"
}


## GY273

---
title: "Raspberry Pi Pico W:"
date: 2023-08-30T23:20:21+01:00
draft: true
tags: ["Self-Hosting"]
---



Yes, you can use the GY-273 sensor with the Raspberry Pi Pico. **The GY-273 is a magnetometer sensor** that measures the strength and direction of magnetic fields. It can be used to create a digital compass, or to detect the presence of magnetic objects.

The GY-273 is compatible with the Raspberry Pi Pico's I2C bus. To connect the GY-273 to the Pico, you will need to use a four-wire cable. The following table shows the connections:

```py
GY-273	Raspberry Pi Pico
VCC	3.3V
GND	GND
SCL	SCL
SDA	SDA
```


The GY-273 is a digital compass module based on the QMC5883L chip. It is a triple-axis magnetometer that can measure the Earth's magnetic field in three dimensions. The GY-273 has a measuring range of ±1.3 to 8 gauss and a resolution of 0.01 gauss. It is powered by a 3 to 5V supply and communicates using the I2C protocol.

The GY-273 is commonly used in robotics, drones, and other applications that require accurate orientation sensing. It can also be used in navigation systems, such as GPS receivers.

Here are some of the features of the GY-273 sensor:

Triple-axis magnetometer: Measures the Earth's magnetic field in three dimensions.
Measuring range of ±1.3 to 8 gauss: Can measure weak to strong magnetic fields.
Resolution of 0.01 gauss: Accurately measures small changes in the magnetic field.
Powered by a 3 to 5V supply: Widely compatible with different power sources.
Communicates using the I2C protocol: Easy to interface with microcontrollers.
If you are looking for a precise and versatile magnetometer sensor, the GY-273 is a good option to consider.

Here are some of the applications of the GY-273 sensor:

Robotics: Used to determine the orientation of robots, such as self-driving cars and drones.
Navigation: Used in GPS receivers and other navigation systems to determine the position of an object.
Avionics: Used in aircraft to determine the attitude of the aircraft.
Marine: Used in ships and boats to determine the heading of the vessel.
Surveying: Used to measure the magnetic field of the Earth.
Geology: Used to study the magnetic properties of rocks and minerals.
I hope this helps!

## KY008

<https://www.youtube.com/watch?v=KX_-MPOJNXY>

The **KY-008 sensor is a laser transmitter module** that emits a red laser beam. It can be used for a variety of projects, including:

Remote signaling: The laser beam can be used to send signals to a receiver module. This can be used to create a simple remote control, or to create a sensor that detects the presence of an object.
Line following: The laser beam can be used to create a line following robot. The robot can be programmed to follow the laser beam, even if it is curved or broken.
Distance measurement: The laser beam can be used to measure the distance to an object. This can be done by measuring the time it takes for the laser beam to reflect back to the receiver module.
Obstacle avoidance: The laser beam can be used to create an obstacle avoidance sensor. The sensor can be programmed to detect obstacles and avoid them.
Security system: The laser beam can be used to create a security system. The system can be programmed to sound an alarm if the laser beam is interrupted.
The KY-008 sensor is a versatile device that can be used for a variety of projects. It is important to note that the laser beam emitted by the KY-008 sensor can be harmful to eyes, so it should be used with caution.

Here are some additional things to keep in mind when using the KY-008 sensor:

The laser beam is emitted in a straight line, so it is important to make sure that there are no obstacles in the way.
The laser beam can be affected by sunlight and other bright light sources, so it is important to use the sensor in a dark environment.
The laser beam can be dimmed by adjusting the resistor on the module.



Yes, you can use the KY-008 sensor with the Raspberry Pi Pico. The Pico has a 5V output pin that can be used to power the laser module. The laser module has two pins: VCC and GND. VCC should be connected to the 5V pin on the Pico and GND should be connected to the ground pin on the Pico.

Here is a simple circuit that you can use to connect the KY-008 sensor to the Raspberry Pi Pico:

VCC (laser) ---> 5V (Pico)
GND (laser) ---> GND (Pico)
Once the laser module is connected to the Pico, you can control it using software. There are many tutorials available online that show you how to do this.

Please note that the laser beam emitted by the KY-008 sensor can be harmful to eyes, so it should be used with caution. It is important to make sure that the laser beam is not pointed directly at anyone.




### DHT11 - Blink IoT Platform




## ESP32 + MLX90614

<https://www.youtube.com/watch?v=HpsvNIAtjm4>


## car battery

<https://www.youtube.com/watch?v=VnGRFwDrLHo>