from django.contrib import admin
from .models import FollowerBank, InstaAccounts, MediaBank, Process, ProcessLog, Violator
# Register your models here.


admin.site.register(InstaAccounts)
admin.site.register(Process)
admin.site.register(ProcessLog)
admin.site.register(FollowerBank)
admin.site.register(Violator)
admin.site.register(MediaBank)