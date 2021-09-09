#!/usr/bin/env python

import mapper as mpr

# Set up libmapper objects.
dev = mpr.device("producer")
sig_out = dev.add_signal(mpr.DIR_OUT, "output2d", 2, mpr.FLT, None, 0, 100)

# Set up counter variables
new_value = 0.0
direction = 1

while(True):
    dev.poll(100)
    
    new_value = round(new_value + 0.1 * direction, 1)
    
    # Ensure that the value is always between 0 and 1 inclusive
    if new_value == 0.0 or new_value == 1.0:
        direction *= -1
    
    print([new_value, new_value])
    sig_out.set_value([new_value, new_value])