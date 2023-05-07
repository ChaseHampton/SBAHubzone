from dataclasses import dataclass

@dataclass
class Batch():
    recs: iter
    limit: int
    offset: int

    def __init__(self, recs:iter=None, limit:int = 1000, offset:int = 1000):
        self.recs = recs
        self.limit = limit
        self.offset = offset
