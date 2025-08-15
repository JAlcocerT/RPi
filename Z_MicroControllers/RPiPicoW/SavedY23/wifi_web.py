import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests


# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


# Fill in your network name (ssid) and password here:
ssid = 'HUAWEI P30'
password = 'mokradupa68'
wlan.connect(ssid, password)




# Example 1. Make a GET request for google.com and print HTML
# Print the html content from google.com
print("1. Querying the web")
#r = urequests.get("https://fossengineer.com")
#print(r.content)

r = urequests.get("http://date.jsontest.com/")
print(r.json())
print(r.json()['time'])

