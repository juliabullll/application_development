import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
import os


rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
broker = RabbitBroker(rabbitmq_url)
app = FastStream(broker)


@broker.subscriber("order_queue")
async def handle(msg):
    print(f"Received message: {msg}")
    return {"processed": True}


@app.after_startup
async def test_publish():
    await broker.publish("Test message", queue="order_queue")
    print("Test message published")


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())