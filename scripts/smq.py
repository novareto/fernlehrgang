from kombu import Connection
import json


with Connection('amqp://vlw:vlw@localhost:5672//') as conn:
    simple_queue = conn.SimpleQueue('vlwd.status')
    message = simple_queue.get(block=True, timeout=1)
    print(message)
    simple_queue.close()
