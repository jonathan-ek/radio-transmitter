import json
import sqlite3
import threading
import time

from transmitter import transmit
from shared_state import queue
from mqtt_service import run_client
from config import DB_NAME


def handle_queue():
    while True:
        if queue.empty():
            time.sleep(1)
        else:
            try:
                [_payload, transmitter_gpio, rounds] = queue.get()
                transmit(_payload, transmitter_gpio, rounds)
                time.sleep(1)
            except:
                pass

def resend_scheduler():
    while True:
        time.sleep(300)
        resend()

def resend():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM state")
    states = cur.fetchall()
    for state in states:
        queue.put((json.loads(state[2]), state[3], state[4]))
    con.close()

if __name__ == '__main__':
    init_con = sqlite3.connect(DB_NAME)
    init_cur = init_con.cursor()
    init_cur.execute("CREATE TABLE IF NOT EXISTS state(id, state, payload, transmitter_gpio, rounds)")
    init_con.commit()
    init_con.close()

    t = threading.Thread(target=resend_scheduler)
    t.daemon = True
    t.start()

    t2 = threading.Thread(target=handle_queue)
    t2.daemon = True
    t2.start()
    run_client()
