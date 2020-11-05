from telethon.sync import TelegramClient, connection
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import csv


def loadUser(id):
    api_id = 2720778
    api_hash = 'bc4216381cb7f3ceb3275baf6f8c1566'
    phone = '+5355282225'
    client = TelegramClient(
        phone,
        api_id,
        api_hash,
        # Use one of the available connection modes.
        # Normally, this one works with most proxies.
        connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,

        # Then, pass the proxy details as a tuple:
        #     (host name, port, proxy secret)
        #
        # If the proxy has no secret, the secret must be:
        #     '00000000000000000000000000000000'
        proxy=('proxy.digitalresistance.dog', 443, 'd41d8cd98f00b204e9800998ecf8427e')
    )
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))

    chats = []
    last_date = None
    chunk_size = 1000
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
            # if chat.megagroup == True:
            if chat.id == id:
                target_group = chat
        except:
            continue

    print('Fetching Members...')
    all_participants = []
    all_participants = client.get_participants(target_group, aggressive=True)

    print('Saving In file...')
    with open("members.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for user in all_participants:
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash,
                             name, target_group.title, target_group.id])
    print('Members scraped successfully.')
