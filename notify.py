#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Edilson Alzemand
 
import pynotify
pynotify.init("Aplicativo")
notify = pynotify.Notification("Olá Edilson, em que eu posso ajudar?", "", "/home/edilson/Projetos/ubi-virtual-assistant/ubi.svg")

notify.show()

