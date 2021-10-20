import mcpi.minecraft as m
import TwitchAPI as twitch
import threading
from time import sleep
import random

def run():
    print("Connecting to twitch servers...")
    mc = m.Minecraft.create()

    s = twitch.connect()
    twitch.sendMessage(s, "#robertjn_dev", "[BOT] Connected to twitch servers! This is an interactive minecraft game.")
    twitch.sendMessage(s, "#robertjn_dev", "[BOT] Try using !bomb.")

    # region threads
    d = {}
    thread = threading.Thread(target=twitch.checkChat, args=(s, d,))
    thread.start()

    while True:
        sleep(0.1)
        if not thread.is_alive():
            if d != {}:
                lastmessage = d["message"]
                lastsender = d["sender"]
                print(lastsender, ":", lastmessage)
                if lastmessage == "!bomb":
                    mc.postToChat("Warning! TNT incoming!")
                    x, y, z = mc.player.getPos()
                    mc.spawnEntity(x, y+20, z, 20)

                elif lastmessage == "!attack":
                    x, y, z = mc.player.getPos()
                    scounter = 0
                    for i in range(0, 100):
                        x = round(x + random.randrange(-5, 5))
                        y = round(y + random.randrange(-2, 5))
                        z = round(z + random.randrange(-5, 5))
                        if mc.getBlock(x, y, z) == 0 and mc.getBlock(x, y+1, z) == 0:
                            mc.spawnEntity(x,y,z,5)
                            scounter += 1
                            if scounter >= 5:
                                break

                elif lastmessage == "!ghost":
                    x, y, z = mc.player.getPos()
                    mc.spawnEntity(x, y + 5, z, 35)

            d = {}
            thread = threading.Thread(target=twitch.checkChat, args=(s, d,))
            thread.start()

