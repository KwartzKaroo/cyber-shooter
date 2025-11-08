# This file is where all static binary data is loaded from files

import pickle

GUN_OFFSETS = pickle.loads(open('data/guns/offsets', 'rb').read())
GUN_ATTRIBUTES = pickle.loads(open('data/guns/attributes', 'rb').read())
HAND_OFFSETS = {
    '1': pickle.loads(open('data/hand offsets/1', 'rb').read()),
    '2': pickle.loads(open('data/hand offsets/2', 'rb').read()),
    '3': pickle.loads(open('data/hand offsets/3', 'rb').read()),
}
