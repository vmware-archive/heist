#!/usr/bin/env python3
import pop.hub

def start():
    hub = pop.hub.Hub()
    hub.pop.sub.add('heist.heist')
    hub.heist.init.start()


start()
