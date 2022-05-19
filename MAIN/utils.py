import json
from instagrapi import Client
from time import sleep
import random
import re
from .models import ProcessLog, Process, FollowerBank, Violator, MediaBank, InstaAccounts
from instagrapi.mixins.challenge import ChallengeChoice



def get_user_security_code(username):
    account = InstaAccounts.objects.get(username=username)
    return account.last_security_code


def solve_security_code_issue(username):
    current_process = Process.objects.get(account__username=username)
    ProcessLog.objects.create(process=current_process, message="Solving security code challenges..")
    ProcessLog.objects.create(process=current_process, message="You have 20 seconds to enter the security code")
    sleep(30)
    security_code = get_user_security_code(username)
    ProcessLog.objects.create(process=current_process, message=f"Security code is {security_code}")
    if security_code:
        return security_code
    return None

def solve_security_code_issue_with_account(username):
    current_process = Process.objects.get(account__username=username)
    security_code = get_user_security_code(username)
    if security_code:
        ProcessLog.objects.create(process=current_process, message=f"Security code is {security_code}")
        return security_code
    return None


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return solve_security_code_issue(username)
    elif choice == ChallengeChoice.EMAIL:
        return solve_security_code_issue(username)
    return False
        

def clean(word):    
    new_word = [word1 for word1 in word.split() if not word1.startswith('@') ]
    new_word = " ".join(new_word)
    new_word = " ".join(re.findall("[a-zA-Z]+", new_word))
    return new_word.lower()


def is_insane(main, text):
    """
    Check if text matches main text by 80%
    """
    main = main.lower()
    text = text.lower()
    
    match_counter = 0
    for word in text.split():
        if word in main:
            match_counter += 1
    if match_counter / len(text.split()) > 0.7:
        return True
    return False


def change_password_handler(username):
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 8))

    current_process = Process.objects.get(account__username=username)
    ProcessLog.objects.create(process=current_process, message=f"Solved security, password is now {password}")
    
    return password


def remove_last_verification_code(username):
    account = InstaAccounts.objects.get(username=username)
    account.last_security_code = None
    account.save()
    return True

def auth(USERNAME, PASSWORD, running_process):
    remove_last_verification_code(USERNAME)
    auth_account = InstaAccounts.objects.get(username=USERNAME)
    cl = Client()
    if auth_account.has_two_factor:
        cl.challenge_code_handler = challenge_code_handler
        cl.change_password_handler = change_password_handler
        two_factor_auth = solve_security_code_issue_with_account(USERNAME)
        retry = 0
        while not two_factor_auth and retry <= 30:
            ProcessLog.objects.create(process=running_process, message=f"Please insert your 2FA auth token...")
            two_factor_auth = solve_security_code_issue_with_account(USERNAME) 
            sleep(3)
            retry += 1          
        ProcessLog.objects.create(process=running_process, message=f"Filling {two_factor_auth} as the authentication code")
        cl.login(USERNAME, PASSWORD, verification_code=two_factor_auth)    
    else:
        cl.change_password_handler = change_password_handler
        cl.challenge_code_handler = challenge_code_handler
        cl.login(USERNAME, PASSWORD)
    return cl
    


def scrape_followers(USERNAME, PASSWORD, max_follower, p_id):
    max_follower = int(max_follower)
    running_process = Process.objects.get(id=p_id) 
    cl = auth(USERNAME, PASSWORD, running_process)
    user_id = cl.user_id
    ProcessLog.objects.create(process=running_process, message="Accessing Intagram Account..")
    sleep(3) # Delay to mimic user
    all_followers = cl.user_followers(user_id , amount= max_follower).keys()
    recent_followers = list(all_followers)
    bundle = json.dumps(recent_followers)    
    FollowerBank.objects.get_or_create(process=running_process, followers=bundle)    
    ProcessLog.objects.create(process=running_process, message=f"{len(recent_followers)} followers were targetted for sanitization")
    print("done scraping followers")
    return True



def scrape_offensive_comments(USERNAME, PASSWORD, p_id):
    running_process = Process.objects.get(id=p_id) 
    offensive_word = running_process.account.phrase.lower()
    cl = auth(USERNAME, PASSWORD, running_process)
        
    ProcessLog.objects.create(process=running_process, message="Accessing Intagram Account..")
    sleep(random.randint(5,10)) # Delay to mimic user
    ProcessLog.objects.create(process=running_process, message="The process may take a very long time to complete. You can check back later.")
    """
        Main function to scrape offensive comments
    """    
    list_of_followers = FollowerBank.objects.get(process=running_process).followers
    list_of_followers = json.loads(list_of_followers)
    ProcessLog.objects.create(process=running_process, message="Retrieving followers from last journey..")
    
    """
        Generate medias from media bank
        if process exists.
    """
    all_media_pk = []
    try:
        all_media_pk = MediaBank.objects.get(process=running_process).media
        all_media_pk = json.loads(all_media_pk)
    except:
        all_media_pk = []
        ProcessLog.objects.create(process=running_process, message="No post found in media cache. Searching for new ones.")
            
    if list_of_followers and not all_media_pk:
        count = len(list_of_followers)
        for my_follower in list_of_followers:
            recent_20_media = cl.user_medias(int(my_follower), amount= 20)
            recent_20_media_pk = [media.pk for media in recent_20_media]
            all_media_pk = [*all_media_pk, *recent_20_media_pk]
            message = f"Done with a follower with id {my_follower} . Sleeping a little..." 
            print(message)
            ProcessLog.objects.create(process=running_process, message=message)
            count = count - 1
            counter = f"{count} item(s) remaining"
            ProcessLog.objects.create(process=running_process, message=counter)
            
            sleep(random.randint(8,20))
    
    ProcessLog.objects.create(process=running_process, message="Checking for offensive comments..")
    MediaBank.objects.create(process=running_process, media=json.dumps(all_media_pk))
    sleep(random.randint(5,50)) # Delay to mimic user
    if all_media_pk:
        for post_pk in all_media_pk:
            comments = cl.media_comments(int(post_pk), amount = 300)
            main = offensive_word.lower()
            for comment in comments:
                if clean(comment.text):
                    if is_insane(main, clean(comment.text)) :
                    
                        print(f"{comment.user.username} violated, now blacklisted.")
                        ProcessLog.objects.create(process=running_process, message=f"{comment.user.username} violated, now blacklisted.")
                        try:
                            Violator.objects.create(process=running_process, name=comment.user.username)
                        except Exception:
                            ProcessLog.objects.create(process=running_process, message="Already blacklisted")
                    else:
                        print(f"{comment.text} ==> is clean")
                        ProcessLog.objects.create(process=running_process, message=f"{comment.user.username} is innocent.")
        ProcessLog.objects.create(process=running_process, message="Laying low to avoid detection.. ;-) ")
        print("sleeping before next media")
        sleep(random.randint(5,15))
    else:
        ProcessLog.objects.create(process=running_process, message="No media to check")
    
    return True
            


def block_list_of_violators(USERNAME, PASSWORD, p_id):
    ProcessLog.objects.create(process=Process.objects.get(id=p_id), message="Accessing Intagram Account..")
    running_process = Process.objects.get(id=p_id) 
    cl = auth(USERNAME, PASSWORD, running_process)
    
    """
        Get lists of Violators from process and block them
    """
    
    current_process = Process.objects.get(id=p_id)
    violators = Violator.objects.filter(process=current_process)
        
    if not violators:
        ProcessLog.objects.create(process=current_process, message="No violators to block")
        return True
    ProcessLog.objects.create(process=current_process, message="Accessing Instagram Account..")    
    
    estimated_time = round(((len(violators) * 60)/3600), 5)
    ProcessLog.objects.create(process=current_process, message=f"this will take about {estimated_time} hour(s)")  
    
    for violator in violators:
        user_id = cl.user_id_from_username(violator.name)
        block_status = cl.user_block(user_id)
        
        if block_status:
            ProcessLog.objects.create(process=current_process, message=f"{violator.name} was blocked!")
            Violator.objects.filter(name=violator.name).delete()
        else:
            ProcessLog.objects.create(process=current_process, message=f"{violator.name} was not blocked!")
        sleep_time = random.randint(10,60)
        
        ProcessLog.objects.create(process=current_process, message=f"Laying low for {sleep_time}s to avoid detection...")    
        sleep(sleep_time)
    return True