from insta import check_violators

USERNAME = input("Enter your instagram username >>  ")
PASSWORD = input("Enter your instagram Password >>  ")
max_follower = ""
while not max_follower: 
    try:
        max_follower = input("Enter the maximum numbers of Followers to fetch >>  ") 
        max_follower = int(max_follower)
    except Exception:
        print("only numbers supported, try again")
        max_follower = ""
        
offensive_word = input("type in the offensive word >>  ")
answer = check_violators(USERNAME, PASSWORD, max_follower,offensive_word)
print(answer)