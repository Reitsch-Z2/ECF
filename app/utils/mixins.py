import time

class Upmodel():
    def to_dict(self, list):
        return {k: (getattr(self, k) if k!='date' else getattr(self, k).strftime('%Y-%m-%d')) for k in list}