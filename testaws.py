#!/usr/bin/env python3

import awstool

li = awstool.list_inst()

print("Simple print of ID")
for i in li:
    print(i.id)

bdict = {}

print("Print dict of inst ID + Name")

for i in li:
    bdict[i.tags[0]["Value"]] = i.id

print(bdict)
