from kombu import Connection
import json


results = dict(
    lehrheft_id=1001,
    frage_id=10001,
    gbo_daten="GBO JSON STREAM",
    kursteilnehmer_id=900010
    )


with Connection('amqp://guest:guest@localhost:5672//') as conn:
    simple_queue = conn.SimpleQueue('vlwd.antwort')
    message = json.dumps(results)
    simple_queue.put(message)
    print('Sent: %s' % message)
    simple_queue.close()
