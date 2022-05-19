from email import message
import json
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from ACCOUNT.forms import RegistrationForm  
from django.contrib.auth.decorators import login_required
from .models import InstaAccounts, Process, ProcessLog
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .tasks import start_getting_followers, sanitize_posts,remove_offenders
from InstaBuddy.celery import app as celery_handler

def homepage(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    form = RegistrationForm()
    return render(request, 'homepage.html', {"form": form})

@login_required
def dashboard(request):
    attached_accounts = InstaAccounts.objects.filter(attached_to=request.user)
    context = {"attached_accounts": attached_accounts}
    return render(request, 'dashboard.html', context)


@login_required
@csrf_exempt
def addInstaAccount(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        access_id = body['access_id']
        max_followers = body['max']
        phrase = body['phrase']
        has_two_factor = body['two_factor']
        attached_to = request.user
        if not username or not access_id or not max_followers or not phrase:
            return HttpResponseForbidden("<small>Please fill out all fields<small/>")
        try:
            InstaAccounts.objects.create(username=username, access_id=access_id, max_followers=int(max_followers), phrase=phrase, attached_to=attached_to, has_two_factor=has_two_factor)
            return JsonResponse({
                "message": "success"
            })
        except Exception:
            return HttpResponseForbidden("Invalid Request")       
    return HttpResponseForbidden("Invalid Request")


def account_details_page(request, account_id):
    account = InstaAccounts.objects.get(id=account_id)
    process = None
    try:
        process = Process.objects.get(account=account)
    except Exception:
        process = None
    logs = ProcessLog.objects.filter(process__account=account)
    if account.attached_to != request.user:
        return HttpResponseForbidden("<small>You did not create this account<small/>")
    context = {"account": account, "logs": logs, "process": process}
    return render(request, 'account_details.html', context)

@login_required
@csrf_exempt
def start_journey(request):
    if request.method == "POST":
        id = request.POST["account_id"]
        if not id:
            return HttpResponseForbidden("Invalid Request")
        all_process = Process.objects.all().count()
        if all_process >= 2:
            return JsonResponse({
                "message": "You can only have 2 processes at a time, close or wait for others to finish.",
            })
            
        insta_obj = InstaAccounts.objects.get(id=id)
        try:
            running_process,_ = Process.objects.get_or_create(account=insta_obj)
            running_process.stage = 1
            running_process.save()
            if _:
                log = ProcessLog.objects.create(process=running_process, message="A new journey has started, ID: {}".format(running_process.id))
            return JsonResponse({
                "message": "success"
                })
        except Exception as e:
            return JsonResponse({
                "message": "an error occurred"
            })
        
    return HttpResponseForbidden("Invalid Request")



@login_required
@csrf_exempt
def get_followers(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        account = InstaAccounts.objects.get(id=account_id)
        running_process = Process.objects.get(account=account)
        if  int(running_process.stage) == 1:
            running_process.stage = 2
            running_process.save()
            start_getting_followers.delay(running_process.id)
            ProcessLog.objects.create(process=running_process, message="Mining Followers")
            return JsonResponse({
                "message": "success"
            })
        else:
            return JsonResponse({
              "message": "Error! you have a running process"  
            })
            
    return HttpResponseForbidden("Invalid Request")
        
        
@login_required
@csrf_exempt        
def get_comments(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        account = InstaAccounts.objects.get(id=account_id)
        running_process = Process.objects.get(account=account)
        if  int(running_process.stage) == 3:
            running_process.stage = 4
            running_process.save()
            sanitize_posts.delay(running_process.id)
            ProcessLog.objects.create(process=running_process, message="Mining Comments for each follower")
            return JsonResponse({
                "message": "success"
            })
        else:
            return JsonResponse({
              "message": "Error! you have a running process"  
            })
            
    return HttpResponseForbidden("Invalid Request")        

@login_required
@csrf_exempt
def ban_offenders(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        account = InstaAccounts.objects.get(id=account_id)
        running_process = Process.objects.get(account=account)
        if  int(running_process.stage) == 5:
            running_process.stage = 6
            running_process.save()
            remove_offenders.delay(running_process.id)
            ProcessLog.objects.create(process=running_process, message="Banning Offenders")
            return JsonResponse({
                "message": "success"
            })
        else:
            return JsonResponse({
              "message": "Error! you have a running process"  
            })
            
    return HttpResponseForbidden("Invalid Request")

@csrf_exempt
def delete_process(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        account = InstaAccounts.objects.get(id=account_id)
        running_process = Process.objects.get(account=account)
        running_process.delete()
        return JsonResponse({
            "message": "success"
        })
    return HttpResponseForbidden("Invalid Request")

@login_required
def deleteInstaAcct(request, account_id):
    try:
        account = InstaAccounts.objects.get(id=account_id)
        if account.attached_to != request.user:
            return HttpResponseForbidden("<small>You did not create this account<small/>")
        account.delete()
    except:
        return HttpResponseForbidden("<small>An error occurred<small/>")
    return redirect("/")


@csrf_exempt
def continuos_log_poll(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        try:
            account = InstaAccounts.objects.get(id=account_id)
            running_process = Process.objects.get(account=account)
            logs = ProcessLog.objects.filter(process=running_process)
            logs = list(logs.values_list('message', flat=True))
        
            return JsonResponse({
                "logs": logs
            })
        except:
            return JsonResponse({
                "logs": []
            })
    return HttpResponseForbidden("Invalid Request")

@login_required
@csrf_exempt
def save_insta_security_code(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        code = request.POST["security_code"]
        if not code or not account_id:
            return HttpResponseForbidden("Invalid Request")
        account = InstaAccounts.objects.get(id=account_id)
        if account.attached_to != request.user:
            return HttpResponseForbidden("<small>You did not create this account<small/>")
        account.last_security_code = code
        account.save()
        return JsonResponse({
            "message": "success"
        })
    return HttpResponseForbidden("Invalid Request")

def force_clear_bot(request):
    celery_handler.control.purge()
    #remove all running processes
    Process.objects.all().delete()
    return redirect("/")
