# BackEnd/MongoModels/user.py

class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def to_dict(self):
        return {"name": self.name, "email": self.email, "age": self.age}
