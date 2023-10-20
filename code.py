# This example shows using TCA9548A to perform a simple scan for connected devices
import board
import time
import adafruit_tca9548a
import busio
import adafruit_mlx90640
import busio
import microcontroller
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import terminalio
import adafruit_requests

# Create I2C bus as normal
#2c = board.I2C()  # uses board.SCL and board.SDA
#i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
i2c = busio.I2C(board.SCL1, board.SDA1)
# Create the PCA9546A object and give it the I2C bus
mux = adafruit_tca9548a.PCA9546A(i2c)

#mlx1 = adafruit_mlx90640.MLX90640(mux[0])
mlx2 = adafruit_mlx90640.MLX90640(mux[1])
mlx3 = adafruit_mlx90640.MLX90640(mux[2])
#mlx4 = adafruit_mlx90640.MLX90640(mux[3])

#mlx1.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
mlx2.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
mlx3.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
#mlx4.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
frame = [0] * 768




try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]
location = secrets.get("timezone", None)
TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s" % (aio_username, aio_key)
TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
### Feeds ###

# Setup a feed named 'photocell' for publishing to a feed
#photocell_feed = secrets["aio_username"] + "/feeds/photocell"
QTTemp_feed = secrets["aio_username"] + "/feeds/pitemp"

QTHum_feed = secrets["aio_username"] + "/feeds/pitemp2"



# Setup a feed named 'onoff' for subscribing to changes
onoff_feed = secrets["aio_username"] + "/feeds/onoff"

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % onoff_feed)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(onoff_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()





while True:
    mqtt_client.loop()
    stamp = time.monotonic()
    try:
        mlx2.getFrame(frame)
    except ValueError:
        # these happen, no biggie - retry
        continue
    print("cam 1")
    print(max(frame))

    mqtt_client.publish(pitemp_feed, max(frame))

    try:
        mlx3.getFrame(frame)
    except ValueError:
        # these happen, no biggie - retry
        continue
    print("cam 2")
    print(max(frame))

    mqtt_client.publish(pitemp2, max(frame))
    #print("Sent!")
    # Draw a label

    time.sleep(8)



  # Write your code here :-)
