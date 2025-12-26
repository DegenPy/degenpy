import requests
import time
from getpass import getpass
import random
from kols import KOLS, KOL_IDS
from config import (
    USERNAME, PROMPT_FILE,
    TOPICS, REPLY_ODDS, REPLY_GUY_ODDS, BANGER_ODDS, TWEET_KOL_ODDS,
    MODEL_NAME, TEMPERATURE, TOP_P, REPETITION_PENALTY, MAX_TOKENS
)

# These will be loaded from .env or prompted
PROXY = ""
TWITTERAPI_API_KEY = ""
RUNPOD_ENDPOINT = ""
RUNPOD_API_KEY = ""

def load_env():
    """Load environment variables from .env file"""
    global PROXY, TWITTERAPI_API_KEY, RUNPOD_ENDPOINT, RUNPOD_API_KEY
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "PROXY":
                        PROXY = value
                    elif key == "TWITTERAPI_API_KEY":
                        TWITTERAPI_API_KEY = value
                    elif key == "RUNPOD_ENDPOINT":
                        RUNPOD_ENDPOINT = value
                    elif key == "RUNPOD_API_KEY":
                        RUNPOD_API_KEY = value
    except FileNotFoundError:
        pass  # Will prompt for values

def save_env():
    """Save environment variables to .env file"""
    with open(".env", "w") as f:
        f.write(f"PROXY={PROXY}\n")
        f.write(f"TWITTERAPI_API_KEY={TWITTERAPI_API_KEY}\n")
        f.write(f"RUNPOD_ENDPOINT={RUNPOD_ENDPOINT}\n")
        f.write(f"RUNPOD_API_KEY={RUNPOD_API_KEY}\n")

def prompt_for_env():
    """Prompt user for missing environment variables"""
    global PROXY, TWITTERAPI_API_KEY, RUNPOD_ENDPOINT, RUNPOD_API_KEY
    
    if not PROXY:
        print("PROXY not found in .env")
        PROXY = input("Enter your proxy (http://username:password@ip:port): ").strip()
    
    if not TWITTERAPI_API_KEY:
        print("TWITTERAPI_API_KEY not found in .env")
        TWITTERAPI_API_KEY = getpass("Enter your TwitterAPI.io API key: ").strip()
    
    if not RUNPOD_ENDPOINT:
        print("RUNPOD_ENDPOINT not found in .env")
        RUNPOD_ENDPOINT = input("Enter your RunPod endpoint URL (no trailing /): ").strip()
    
    if not RUNPOD_API_KEY:
        print("RUNPOD_API_KEY not found in .env")
        RUNPOD_API_KEY = getpass("Enter your RunPod API key: ").strip()
    
    save_env()
    print("Credentials saved to .env\n")

def load_system_prompt():
    """Load system prompt from prompt.md file"""
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise Exception(f"Prompt file '{PROMPT_FILE}' not found. Please create it with your system prompt.")

def validate_config():
    """Ensure required config values are set"""
    if not USERNAME:
        raise Exception("USERNAME is not set. Please set your Twitter username in config.py")

SYSTEM_PROMPT = load_system_prompt()

TWEET_SLEEP_TIME = 10 # amount of time to wait between sending each tweet. default 10

TENSE = ["past", "present", "future"]

#COLORS
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[0m"
CYAN = "\033[96m"

def main():
    print(GREEN+r"""
      _                       
     | |                      
   __| | ___  __ _  ___ _ __  
  / _` |/ _ \/ _` |/ _ \ '_ \ 
 | (_| |  __/ (_| |  __/ | | |
  \__,_|\___|\__, |\___|_| |_|
              __/ |           
             |___/                        
    """)

    load_env()
    if not PROXY or not TWITTERAPI_API_KEY or not RUNPOD_ENDPOINT or not RUNPOD_API_KEY:
        prompt_for_env()
    
    validate_config()
    login_cookie = get_login_cookie()
    if not login_cookie:
        email = input("Enter the email associated with your X account: ")
        password = getpass("Enter your X account password: ")
        totp_secret = getpass("Enter the TOTP 2FA secret key for your X account (you must have TOTP 2FA enabled to use zereploi): ")
        login_cookie = twitter_login(email, password, totp_secret)
        if not login_cookie:
            raise Exception("Unable to log in using provided credentials. Exiting.")
        set_login_cookie(login_cookie)
    
    if not get_timestamp():
        set_timestamp()
    
    actions = {"do_replies": REPLY_ODDS, "reply_guy":REPLY_GUY_ODDS, "write_banger": BANGER_ODDS, "tweet_kol": TWEET_KOL_ODDS}
    action_names = list(actions.keys())
    action_weights = list(actions.values())
    
    while True:
        try:
            print(f"{CYAN}💡 CHOOSING NEXT ACTION...")
            match random.choices(action_names, weights=action_weights, k=1)[0]:
                case "do_replies":
                    print(f"{GREEN}\n💬 Decided to check for mentions to reply to\n")
                    do_replies(login_cookie)
                case "reply_guy":
                    print(f"{GREEN}\n🗣️ Decided to check for recent KOL tweets to reply to\n")
                    reply_guy(login_cookie)
                case "write_banger":
                    print(f"{GREEN}\n📝 Decided to write a banger tweet\n")
                    write_banger(login_cookie)
                case "tweet_kol":
                    print(f"{GREEN}\n📣 Decided to tweet @ a KOL\n")
                    tweet_kol(login_cookie)
        except Exception as e:
            print(f"{RED}Action failed: {e}")
        time.sleep(10)

def do_replies(login_cookie):
    print(f"{WHITE}Checking for mentions...\n")
    last_time = get_timestamp()
    set_timestamp()

    tweets = []
    got_all_mentions = False
    cursor = None

    while not got_all_mentions:
        tweetlist, has_next_page, cursor = get_mentions(last_time, cursor)
        if tweetlist:
            tweets.extend(tweetlist)
        if not has_next_page and not cursor:
            got_all_mentions = True
        if len(tweets) < 20:
            got_all_mentions = True
        if got_all_mentions:
            break
    
    for tweet in tweets:
        id = tweet.get("id","")
        text = tweet.get("text","")
        from_user = tweet.get("from_user","")

        if id and text and from_user:
            prompt = SYSTEM_PROMPT+f'''
You are replying to @{from_user}.

Their tweet: "{text}"

Write your reply. One or two sentences max. No quotes around your response. No emojis. No hashtags. No preamble like "Here's my reply:" — just the reply itself.'''
            tweet_text = get_chat_completion(prompt)
            if tweet_text:
                is_note_tweet = len(tweet_text) > 280
                print(f"{WHITE}Sending tweet: {tweet_text} in reply to {id} from @{from_user} where they said {text}")
                send_tweet(login_cookies=login_cookie, tweet_text=tweet_text, reply_to_tweet_id=id, community_id=None, is_note_tweet=is_note_tweet)
            else:
                print(f"{RED}Error reaching runpod inference endpoint")
            time.sleep(TWEET_SLEEP_TIME)
    if tweets == []:
        print(f"{WHITE}No recent mentions found.\n")

def reply_guy(login_cookie):
    print(f"{WHITE}Checking for posts to reply to...\n")

    tweets = []
    tweetlist = get_recents()
    if tweetlist:
        tweets.extend(tweetlist)
    
    for tweet in tweets:
        id = tweet.get("id","")
        text = tweet.get("text","")
        from_user = tweet.get("from_user","")
        kol_prompt = tweet.get("prompt", "")

        if id and text and from_user:
            prompt = SYSTEM_PROMPT+kol_prompt+f'''
You are replying to @{from_user}.

Their tweet: "{text}"

Write your reply. One or two sentences max. No quotes around your response. No emojis. No hashtags. No preamble like "Here's my reply:" — just the reply itself.'''
            tweet_text = get_chat_completion(prompt)
            if tweet_text:
                is_note_tweet = len(tweet_text) > 280
                print(f"{WHITE}Sending tweet: {tweet_text} in reply to {id} from @{from_user} where they said {text}")
                send_tweet(login_cookies=login_cookie, tweet_text=tweet_text, reply_to_tweet_id=id, community_id=None, is_note_tweet=is_note_tweet)
            else:
                print(f"{RED}Error reaching runpod inference endpoint")
            time.sleep(TWEET_SLEEP_TIME)
    if tweets == []:
        print(f"{WHITE}No recent KOL tweets found.\n")

def write_banger(login_cookie):
    topic = random.choice(TOPICS)
    tense = random.choice(TENSE)
    print(f"{WHITE}Writing a banger tweet about {topic}.\n")
    prompt = SYSTEM_PROMPT+f"\n\nWrite a funny banger tweet about {topic}. Write the tweet in the {tense} tense. Reply with only your tweet."
    tweet_text = get_chat_completion(prompt)
    if tweet_text:
        is_note_tweet = len(tweet_text) > 280
        print(f"{WHITE}Tweeting: {tweet_text}")
        send_tweet(login_cookies=login_cookie, tweet_text=tweet_text, reply_to_tweet_id=None, community_id=None, is_note_tweet=is_note_tweet)
    else:
        print(f"{RED}Error reaching runpod inference endpoint")
    time.sleep(TWEET_SLEEP_TIME)

def tweet_kol(login_cookie):
    handle, prompt = random.choice(list(KOLS.items()))
    print(f"{WHITE}Writing a tweet to a KOL: @{handle}.\n")
    full_prompt = SYSTEM_PROMPT+prompt
    tweet_text = get_chat_completion(full_prompt)
    if tweet_text:
        full_tweet_text = f"@{handle} "+tweet_text
        is_note_tweet = len(full_tweet_text) > 280
        print(f"{WHITE}Tweeting: {full_tweet_text}")
        send_tweet(login_cookies=login_cookie, tweet_text=full_tweet_text, reply_to_tweet_id=None, community_id=None, is_note_tweet=is_note_tweet)
    else:
        print(f"{RED}Error reaching runpod inference endpoint")
    time.sleep(TWEET_SLEEP_TIME)

def get_timestamp():
    try:
        with open("last_timestamp", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

def set_timestamp():
    current_time = int(time.time())
    with open("last_timestamp", "w") as f:
        f.write(str(current_time))

def get_replied_ids():
    try:
        with open("replied_ids", "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_id(id):
    with open("replied_ids", "a") as f:
        f.write(id+"\n")

def get_login_cookie():
    try:
        with open("login_cookie", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

def set_login_cookie(login_cookie):
    with open("login_cookie", "w") as f:
        f.write(str(login_cookie))

def twitter_login(email, password, totp_secret):

    url = "https://api.twitterapi.io/twitter/user_login_v2"

    payload = {
        "user_name": USERNAME,
        "email": email,
        "password": password,
        "proxy": PROXY,
        "totp_secret": totp_secret
    }
    headers = {
        "X-API-Key": TWITTERAPI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    res = response.json()

    if response.status_code != 200:
        error_message = res.get("message", "")
        print(f"{RED}Failed to log in: "+error_message)
        raise Exception("Exiting because we can't log in")
    else:
        login_cookie = res.get("login_cookies")
        print(f"{GREEN}Logged in successfully")
        set_login_cookie(login_cookie)
        return login_cookie

def get_mentions(last_time, cursor=None):
    ids_list = get_replied_ids()
    current_time = int(time.time())

    url = "https://api.twitterapi.io/twitter/user/mentions"

    params = {
        "userName" : USERNAME,
        "sinceTime" : last_time,
        "untilTime" : current_time
    }

    if cursor:
        params["cursor"] = cursor

    headers = {"X-API-Key": TWITTERAPI_API_KEY}

    response = requests.get(url, headers=headers, params=params)

    try:
        res = response.json()
    except Exception as e:
        print(f"{RED}Failed to get mentions: {e}")
        return None, None, None

    tweets = res.get("tweets", [])
    has_next_page = res.get("has_next_page", False)
    next_cursor = res.get("next_cursor", "")

    tweetlist = []

    if tweets:
        for tweet in tweets:
            id = tweet.get("id", "")
            text = tweet.get("text", "")
            isReply = tweet.get("isReply", False)
            author = tweet.get("author") or {}
            author_username = ""
            mentioned = tweet.get("inReplyToUsername", "")

            if author:
                author_username = author.get("userName","")
            
            print(f"{WHITE}Potential hit from @{author_username} who mentioned @{mentioned}")

            if id and text and author_username != USERNAME and (mentioned == USERNAME or f"@{USERNAME}" in text) and id not in ids_list:
                save_id(id)
                tweet_info = {
                    "id": id,
                    "text": text,
                    "from_user": author_username
                }
                tweetlist.append(tweet_info)
        
        if not tweetlist:
            print(f"{RED}No mentions found since the last time range")
        else:
            tweetamt = len(tweetlist)
            print(f"{GREEN}Found {tweetamt} tweets to reply to")

    return tweetlist, has_next_page, next_cursor

def get_recents():
    tweetlist = []
    ids_list = get_replied_ids()
    for userName, userId in KOL_IDS.items():
        url = "https://api.twitterapi.io/twitter/user/last_tweets"

        params = {
            "userId": userId,
            "userName": userName,
            "includeReplies": True
        }

        headers = {"X-API-Key": TWITTERAPI_API_KEY}

        response = requests.get(url, headers=headers, params=params)

        try:
            res = response.json()
        except Exception as e:
            print(f"{RED}Failed to get recents: {e}")
            continue

        data = res.get("data", {})
        tweets = data.get("tweets", [])

        if data and tweets:
            tweet = tweets[0]  # just the first one
            id = tweet.get("id", "")
            text = tweet.get("text", "")
            author = tweet.get("author") or {}
            author_username = author.get("userName", "")

            if id and text and author_username == userName and id not in ids_list:
                save_id(id)
                tweetlist.append({
                    "id": id,
                    "text": text,
                    "from_user": author_username,
                    "prompt": KOLS.get(userName, "")
                })
                print(f"{GREEN}Got latest tweet from @{author_username}")

    return tweetlist

def send_tweet(login_cookies, tweet_text, reply_to_tweet_id=None, community_id=None, is_note_tweet=False):

    url = "https://api.twitterapi.io/twitter/create_tweet_v2"

    json = {
        "login_cookies": login_cookies,
        "tweet_text": tweet_text,
        "proxy": PROXY,
        "is_note_tweet": is_note_tweet,
    }

    if reply_to_tweet_id:
        json["reply_to_tweet_id"] = reply_to_tweet_id

    if community_id:
        json["community_id"] = community_id

    headers = {
        "X-API-Key": TWITTERAPI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=json, headers=headers)

    if response.status_code != 200:
        try:
            res = response.json()
            error_message = res.get("message", "")
        except:
            error_message = response.text
        print(f"{RED}Failed to send tweet: "+error_message)

def get_chat_completion(prompt):
    url = RUNPOD_ENDPOINT+"/v1/chat/completions"

    json = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "repetition_penalty": REPETITION_PENALTY,
        "max_tokens": MAX_TOKENS
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+RUNPOD_API_KEY
    }

    response = requests.post(url=url, json=json, headers=headers)
    if response.status_code != 200:
        print(f"{RED}Request failed: {response.status_code}")
        return None

    try:
        res = response.json()
        completed_text = res["choices"][0]["message"]["content"]
        completed_text = completed_text.strip('"')
        return completed_text
    except (KeyError, IndexError, TypeError, ValueError):
        print(f"{RED}Failed to parse response: {response.text}")
        return None

if __name__ == "__main__":
    main()