from kombu import Connection
import json


results = dict(
    teilnehmer_id=443194,
    status="INFO",
    kursteilnehmer_id=1251557,
    typ="ausstattung",
    buero=True, 
    lager=False, 
    verkauf=False, 
    )

results = dict(
    teilnehmer_id=100000,
    statu="1",
    kursteilnehmer_id=900000,
    typ="fortschritt",
    key="3.18",
    title="Minigame1",
    progress=80,
    )

with Connection('amqp://guest:guest@localhost:5672//') as conn:
    simple_queue = conn.SimpleQueue('vlwd.log')
    message = json.dumps(results)
    simple_queue.put(message)
    print('Sent: %s' % message)
    simple_queue.close()
