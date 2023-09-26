import random
import uuid

from locust import HttpUser, TaskSet, task

class Visitor():
    def __init__(self, num_visitors: int):
        self.num_visitors = num_visitors
        self.visitor_id_slices = []
        for count in range (0, num_visitors):
            self.visitor_id_slices.append(str(uuid.uuid4()))
    def get_any_userid(self):
        index = random.randint(0, self.num_visitors)
        return self.visitor_id_slices[index]

visitor = Visitor(100000)
class WebsiteUser(HttpUser):
    @task(1)
    def quote(self):
        userid = visitor.get_any_userid()
        self.client.post("/", {"userid": userid})
