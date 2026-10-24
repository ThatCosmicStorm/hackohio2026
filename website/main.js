const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt';
const topic = 'myhome/esp32s3/led';

const client = mqtt.connect(brokerUrl);

client.on('connect', function () {
    document.getElementById('status').innerText = 'Connected!';
    document.getElementById('status').style.color = 'green';
});

client.on('error', function (err) {
    document.getElementById('status').innerText = 'Connection Error: ' + err;
    document.getElementById('status').style.color = 'red';
});

function sendMQTT(command) {
    client.publish(topic, command);
    console.log('Sent command: ' + command);
}

