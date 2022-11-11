#!/usr/bin/env python3

def readSecret(secretPath):
    with open(secretPath) as f:
        mySecret = f.readline().strip()
        return mySecret

def endify(itr):
        """
        Like enumerate() except returns a bool if this is the last item instead of the number
        """
        itr = iter(itr)
        has_item = False
        ended = False
        next_item = None
        while not ended:
            try:
                next_item = next(itr)
            except StopIteration:
                ended = True
            if has_item:
                yield ended, item
            has_item = True
            item = next_item