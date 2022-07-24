class Upmodel():
    def to_dict(self, list):
        return {k: getattr(self, k) for k in list}