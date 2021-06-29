import threading
import TwitchAPI as twitch
from time import sleep


def demo():
    s = twitch.connect()



    counter = 0
    l = []
    thread = threading.Thread(target=twitch.checkChat, args=(s, l, ))
    thread.start()
    while True:
        sleep(0.01)
        counter += 1
        if counter%100 == 0:
            print(counter)

        if not thread.is_alive():
            if len(l) > 0:
                print(l[0])
            l = []
            thread = threading.Thread(target=twitch.checkChat, args=(s, l,))
            thread.start()


