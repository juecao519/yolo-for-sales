import paho.mqtt.client as mqtt
import json
import threading

class VendingMachineIoTClient:
    def __init__(self, broker, port, client_id, on_command=None, username=None, password=None):
        self.client = mqtt.Client(client_id)
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)
        self.on_command = on_command  # 回调函数
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        print("✅ [IoT] 已连接到MQTT Broker，返回码:", rc)
        client.subscribe("vending/command")  # 订阅云端指令主题

    def on_message(self, client, userdata, msg):
        print("📥 [IoT] 收到云端指令:", msg.topic, msg.payload.decode())
        try:
            command = json.loads(msg.payload.decode())
            if self.on_command:
                self.on_command(command)
        except Exception as e:
            print("❌ [IoT] 指令解析失败:", e)

    def publish_status(self, topic, data):
        payload = json.dumps(data, ensure_ascii=False, indent=2)  # 加上indent=2
        self.client.publish(topic, payload)
        print(f"📤 [IoT] 上报数据到 {topic}:\n{payload}")

    def start(self):
        self.running = True
        threading.Thread(target=self.client.loop_forever, daemon=True).start()

    def stop(self):
        self.running = False
        self.client.disconnect()