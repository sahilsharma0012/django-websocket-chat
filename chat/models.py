from django.db import models

# Room table
class Room(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    
    def __str__(self):
        return self.name
    
# Message Table
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete = models.CASCADE, related_name = "messages")
    sender = models.CharField(max_length = 100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.sender}: {self.content}"