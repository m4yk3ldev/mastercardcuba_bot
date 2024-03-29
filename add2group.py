from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os
import sys
import csv
import traceback
import time
import random

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    print(re+"[!] run python3 setup.py first !!\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('clear')
    client.sign_in(phone, input(gr+'[+] Enter the code: '+re))

os.system('clear')
input_file = sys.argv[1]
users = []
with open(input_file, encoding='UTF-8') as f:
    rows = csv.reader(f, delimiter=",", lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
    ))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue

i = 0
for group in groups:
    print(gr+'['+cy+str(i)+gr+']'+cy+' - '+group.title)
    i += 1

print(gr+'[+] Choose a group to add members')
g_index = input(gr+"[+] Enter a Number : "+re)
target_group = groups[int(g_index)]

all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)
len_user_antes = len(users)
for u in users:
    for p in all_participants:
        if u['id'] == p.id:
            print(f'Borrado {u["username"]} ')
            users.remove(u)
target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

print(f"De {len_user_antes} users quedaron {len(users)} ")
print(gr+"[1] add member by user ID\n[2] add member by username ")
mode = int(input(gr+"Input : "+re))
n = 0

for user in users:
    n += 1
    if n % 5 != 0:
        time.sleep(1)
        try:
            print(f"Adding {user['id']} is {user['name']}")
            if mode == 1:
                if user['username'] == "":
                    continue
                user_to_add = client.get_input_entity(user['username'])
            elif mode == 2:
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                sys.exit(re+"[!] Invalid Mode Selected. Please Try Again.")
            client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print(gr+"[+] Waiting for 1 min - 5 min ")
            time.sleep(random.randrange(60, 300))
        except PeerFloodError:
            print(
                    re+"[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time.")

            print(gr+"[+] Waiting for 5 min - 10 min ")
            time.sleep(random.randrange(300, 600))
        except UserPrivacyRestrictedError:
            print(re+"[!] The user's privacy settings do not allow you to do this. Skipping.")
        except:
            traceback.print_exc()
            print(re+"[!] Unexpected Error")
            continue
    else:
        print(gr+"[+] Warning pass 6 min-10 min ")
        time.sleep(random.randrange(300, 600))
