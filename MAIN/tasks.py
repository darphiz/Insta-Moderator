from unicodedata import name
from celery.decorators import task
from time import sleep
from .models import Process, ProcessLog, Violator
from .utils import scrape_followers, scrape_offensive_comments, block_list_of_violators,solve_security_code_issue

@task(name='get follower')
def start_getting_followers(process_id):
    max_retry = 3
    retry = 1    
    while retry <= max_retry:
        try:
            running_process = Process.objects.get(id=process_id)

            print("Start fetching followers")
            
            USERNAME = running_process.account.username
            PASSWORD = running_process.account.access_id
            max_follower =  running_process.account.max_followers
            p_id = running_process.id
            scrape_followers(USERNAME, PASSWORD, max_follower, p_id)
            
            running_process = Process.objects.get(id=process_id)
            running_process.stage = 3
            running_process.save()
            ProcessLog.objects.create(process=running_process, message=f"Done Mining Followers, refresh page to see results")
            print("Finished fetching followers")
            return
        except Exception as e:
            try:
                ProcessLog.objects.create(process=running_process, message=e)
                ProcessLog.objects.create(process=running_process, message="Retrying..")
            except:
                pass
            retry += 1   
            continue
    try:
        ProcessLog.objects.create(process=running_process, message="An error occured, Refresh to see next action...")
        running_process = Process.objects.get(id=process_id)
        running_process.stage = 7
        running_process.save()
    except:
        return

    

@task(name="Sanitize Posts")
def sanitize_posts(process_id):
    print("getting offensive comments")
    max_retry = 3
    retry = 1
    while retry <= max_retry:
        try:
            running_process = Process.objects.get(id=process_id)        
            USERNAME = running_process.account.username
            PASSWORD = running_process.account.access_id
            p_id = running_process.id
            
            scrape_offensive_comments(USERNAME, PASSWORD, p_id)
            
            running_process = Process.objects.get(id=process_id)
            running_process.stage = 5
            running_process.save()
            total_violators = Violator.objects.filter(process=running_process).count()
            ProcessLog.objects.create(process=running_process, message=f"Done Sanitizing, {total_violators} offensive comments were found, refresh to see next step")
            return
        except:
            retry = retry + 1
            continue
    
    try:
        ProcessLog.objects.create(process=running_process, message="An error occured, Refresh to see next action...")
        running_process = Process.objects.get(id=process_id)
        running_process.stage = 3
        running_process.save()
    except:
        return

    return

@task(name="ban offenders")
def remove_offenders(process_id):
    max_retry = 3
    retry = 1
    running_process = Process.objects.get(id=process_id)
    while retry <= max_retry:
        try:
            print("banning offenders")
            USERNAME = running_process.account.username
            PASSWORD = running_process.account.access_id
            p_id = running_process.id
            block_list_of_violators(USERNAME, PASSWORD, p_id)
            running_process = Process.objects.get(id=process_id)
            running_process.stage = 7
            running_process.save()
            ProcessLog.objects.create(process=running_process, message="all offenders were banned, refresh to see next step")
            return
        except Exception as e:
            ProcessLog.objects.create(process=running_process, message=e)
            retry = retry + 1
            continue
    try:
        ProcessLog.objects.create(process=running_process, message="An error occured, Refresh to see next action...")
        running_process = Process.objects.get(id=process_id)
        running_process.stage = 4
        running_process.save()
    except:
        return
