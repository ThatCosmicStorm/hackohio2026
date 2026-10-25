const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt';
const topic = 'myhome/esp32s3/led';

const client = mqtt.connect(brokerUrl);

function sendMQTT(command) {
    client.publish(topic, command);
    console.log('Sent command: ' + command);
}

const rings = document.querySelectorAll(".progress-ring");

function setRing(ring, value) {
  const pct = Math.max(0, Math.min(100, Number(value)));
  if (Number.isNaN(pct)) return;

  ring.style.setProperty("--pct", pct);
  ring.querySelector(".round-button").textContent = Math.round(pct) + "%";

  // Optional: colour by level
  let color = "#4caf50";
  if (pct <= 50) color = "#ff9800";
  if (pct <= 20) color = "#f44336";
  ring.style.setProperty("--fill", color);
}


client.on("connect", () => {
  document.getElementById("status").textContent = "Connected";
  rings.forEach(ring => client.subscribe(ring.dataset.topic));
});

client.on("message", (topic, message) => {
  rings.forEach(ring => {
    if (ring.dataset.topic === topic) setRing(ring, message.toString());
  });
});

function sendMQTT(msg) {
  client.publish("bottle/command", msg);
}



// ---- Mode button ----
const modes = [
  { label: "Off", value: "mode1" },
  { label: "Low", value: "mode2" },
  { label: "Medium", value: "mode3" },
  { label: "High", value: "mode4" }
];
let modeIndex = 0;

const modeButton = document.getElementById("mode-button");

function showMode(i) {
  modeIndex = i % modes.length;
  modeButton.textContent = modes[modeIndex].label;
}

modeButton.addEventListener("click", () => {
  showMode(modeIndex + 1);                                   // next mode, wraps to the first
  client.publish("bottle/mode", modes[modeIndex].value, { retain: true });
});

showMode(0);

client.on("connect", () => {
  client.subscribe("bottle/mode");
});

client.on("message", (topic, message) => {
  if (topic === "bottle/mode") {
    const i = modes.findIndex(m => m.value === message.toString());
    if (i !== -1) showMode(i);
  }
});