# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone

# class Message(models.Model):
#     sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
#     receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
#     subject = models.CharField(max_length=255)
#     body = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Message from {self.sender} to {self.receiver}"
