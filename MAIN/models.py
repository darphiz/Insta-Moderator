from concurrent.futures import process
from enum import unique
from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class InstaAccounts(models.Model):
    username = models.CharField(max_length=200, unique=True)
    access_id = models.CharField(max_length=200)
    max_followers = models.IntegerField(default=2)
    phrase = models.CharField(max_length=200, default="")
    attached_to = models.ForeignKey(User,on_delete=models.CASCADE, related_name="insta", blank=True, null=True)
    last_security_code = models.CharField(max_length=200, default="", blank=True, null=True)
    has_two_factor = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
        
class Process(models.Model):
    account = models.OneToOneField(InstaAccounts, on_delete=models.CASCADE, related_name="process")
    ended = models.BooleanField(default=False)
    stage = models.IntegerField(default=0)
    
    
class ProcessLog(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="logs")
    message = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
    
class FollowerBank(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="followers")
    followers = models.TextField()
    def __str__(self):
        return self.followers
    
class Violator(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="violators")
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name
    
class MediaBank(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="media")
    media = models.TextField()
    def __str__(self):
        return self.media