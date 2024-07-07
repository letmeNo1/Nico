import tempfile



class NicoImage:
    def __init__(self, udid):
        self.udid = udid
        self.source_image_path = tempfile.gettempdir() + "/test.png"

