from instagrapi import Client
from time import sleep
import random
from os import walk
import re

def clean(word):    
    word1 = " ".join(re.findall("[a-zA-Z]+", word))
    return word1.lower()

def load_cache(name):
    with open(f'scrap_cache/{name}.txt', 'r') as f:
        items = f.readlines()  
        items = [item.strip() for item in items]
    return items


def cache_item(name, items):
    with open(f'scrap_cache/{name}.txt', 'w') as f:
        for item in items:
            f.write("%s\n" % item)    


def check_cache(log_name):
    log_present = False
    filenames = next(walk("scrap_cache"), (None, None, []))[2] 
    if filenames:
        for filename in filenames:
            if filename == log_name:
                    log_present = True
    return log_present

def is_insane(main, sub_split):
    ind = -1
    for word in sub_split:
        ind = main.find(word, ind+1)
        if ind == -1:
            return False
    return True



def check_violators(USERNAME, PASSWORD, max_follower,offensive_word):
    max_retry = 3
    retry = 1
    violators = []
    while retry <= max_retry:
        try:
            ##############################AUTH############################
        
            cl = Client()
            cl.login(USERNAME, PASSWORD)
            user_id = cl.user_id
            sleep(2) # Delay to mimic user
            print("Log in successful")
            ###################Introduces [cl] variable#####################



            #################Getting lists of followers#######################
            list_of_followers = []

            if not check_cache("followers.txt"):
                print("Fetching recent followers")
                print(f"is id {user_id}")
                all_followers = cl.user_followers(user_id , amount= 0).keys()
                print(f"has {len(all_followers)} followers")
                recent_followers = list(all_followers)[:max_follower]
                cache_item("followers", recent_followers)
                list_of_followers = recent_followers
            else:
                print("getting cached followers")
                list_of_followers = load_cache("followers")
            print("sleeping for 10 seconds")
            sleep(10)
            #############################Introduces [list_of_followers] variable###########################


            #######################################Getting posts from each follower #######################
            all_media_pk = []
            if list_of_followers:
                count = len(list_of_followers)
                for my_follower in list_of_followers:
                    recent_20_media = cl.user_medias(int(my_follower), amount= 20)
                    recent_20_media_pk = [media.pk for media in recent_20_media]
                    all_media_pk = [*all_media_pk, *recent_20_media_pk]
                    print(f"{my_follower} done. Sleeping a little...")
                    count = count - 1
                    print(f"{count} item(s) remaining")
                    sleep(random.randint(8,13))
            ######################## introduces recent_20_media_pk ###########################################


            ################################### sanitizing each comment ######################################################
            violators = []
            if all_media_pk:
                for post_pk in all_media_pk:
                    comments = cl.media_comments(int(post_pk), amount = 300)
                    main = offensive_word.lower()
                    for comment in comments:
                        if clean(comment.text):
                            if is_insane(main, clean(comment.text)) :
                            
                                print(f"{comment.user.username} violated, now blacklisted.")
                                violators.append(comment.user.pk)

                                print(f"{comment.text} ==> is bad")
                            else:
                                print(f"{comment.text} ==> is clean")
                print("sleeping before next media")
                sleep(random.randint(5,15))
                break;
        except Exception as e:
            print(e)
            the_time = random.randint(5,15 * retry) 
            print(f"an error occurred, retrying ....Wait for {the_time}s")
            retry = retry + 1
            sleep(the_time)
            continue        
    return violators
