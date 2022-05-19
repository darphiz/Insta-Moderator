import random

def change_password_handler(username):
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 10))

    # current_process = Process.objects.get(account__username=username)
    # ProcessLog.objects.create(process=current_process, message=f"Solved security, password is now {password}")
    
    return password


change_password_handler