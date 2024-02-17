#include <stdio.h>
#include <stdlib.h>
#include "MQTTClient.h"

#define ADDRESS     "tcp://192.168.3.200:1883"
#define CLIENTID    "ExampleClientPub"
#define TOPIC       "c/mqtt"
#define PAYLOAD     "Hello from C!"
#define QOS         1
#define TIMEOUT     10000L

// int main(int argc, char* argv[]) {
//     // MQTTClient declaration and other code for connecting, publishing, and disconnecting
// }

int main(int argc, char* argv[]) {
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    MQTTClient_deliveryToken token;
    int rc;

    // Initialize the client
    MQTTClient_create(&client, ADDRESS, CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    // Connect to the MQTT broker
    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        printf("Failed to connect, return code %d\n", rc);
        exit(-1);
    }

    // Prepare and publish the message
    pubmsg.payload = PAYLOAD;
    pubmsg.payloadlen = strlen(PAYLOAD);
    pubmsg.qos = QOS;
    pubmsg.retained = 0;
    MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
    printf("Waiting for up to %ld seconds for publication of %s\n"
           "on topic %s for client with ClientID: %s\n",
           TIMEOUT / 1000, PAYLOAD, TOPIC, CLIENTID);
    rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
    printf("Message with delivery token %d delivered\n", token);

    // Disconnect
    MQTTClient_disconnect(client, 10000);
    MQTTClient_destroy(&client);
    return rc;
}
