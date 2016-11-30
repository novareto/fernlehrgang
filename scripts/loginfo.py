from kombu import Connection
import json


results = dict(
    teilnehmer_id=100000,
    status="INFO",
    type="I AM AN INFO MESSAGE FROM MQ!",
    kursteilnehmer_id=900010
    )


with Connection('amqp://guest:guest@localhost:5672//') as conn:
    simple_queue = conn.SimpleQueue('vlwd.log')
    message = json.dumps(results)
    simple_queue.put(message)
    print('Sent: %s' % message)
    simple_queue.close()
