import os
import re

class UiObject:
    def __init__(self, root, udid, func,**query ):
        self.root = root
        self.udid = udid
        self.func = func
        self.query = query
        self.close_keyboard()

    
