import json

class DocumentItem:
    
    def __init__(self, char, position):
        self.char = char
        self.position = position

    def to_json(self):
        return json.dumps({"char": self.char, "position": self.position})
    
    def to_dict(self):
        return {"char": self.char, "position": self.position}