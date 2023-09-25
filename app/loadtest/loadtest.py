import random
import uuid

from locust import HttpLocust, TaskSet, task

class Visitor():
    def __init__(self, num_visitors: int):
        self.num_visitors = num_visitors
        self.visitor_id_slices = []
        for count in range (0, num_visitors):
            self.visitor_id_slices.append(str(uuid.uuid4()))
    def get_any_userid(self):
        index = random.randint(0, self.num_visitors)
        return self.visitor_id_slices[index]

class WebsiteTasks(TaskSet):
    visitor = Visitor(100)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task(1)
    def quote(self):
        userid = visitor.get_any_userid()
        self.client.post("/", {"userid": userid})

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 2
    max_wait = 5
