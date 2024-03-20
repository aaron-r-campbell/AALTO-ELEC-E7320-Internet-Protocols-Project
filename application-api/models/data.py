import json

class DocumentItem:
    
    def __init__(self, value, position):
        self.value = value
        self.position = position

    def to_json(self):
        return json.dumps({"value": self.value, "position": self.position})
    
    def to_dict(self):
        return {"value": self.value, "position": self.position}