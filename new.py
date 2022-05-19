from telethon.sync import TelegramClient,events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.types import InputPeerEmpty
from datetime import datetime, timedelta
import asyncio
import re
import sys

scheduler_list = []



def make_schedule(data):
    hour_minute = data.split(' ')[0]
    hour_minute = datetime.strptime(hour_minute, '%H:%M')
    delayed_hour = hour_minute - timedelta(minutes=1)
    scheduler_list.append({"signal": data, "time": delayed_hour.strftime('%H:%M')})
    print(f"Scheduled: {data} - {delayed_hour.strftime('%H:%M')}")


def get_telegram_groups(client):
    chats = []
    last_date = None
    chunk_size = 200
    groups=[]

    result = client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=chunk_size,
                hash = 0
            ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            group_data = {}
            group_data['username'] = chat.username
            group_data['id'] = chat.id
            group_data['hash'] = chat.access_hash
            group_data['title'] = chat.title
            groups.append(group_data)
        except:
            continue
    return groups

telegram_phone = input('Telegram phone number: ')
telegram_client = TelegramClient(telegram_phone, api_id=10662829, api_hash='38bdd213b2ed9ea288d998709720136e')
telegram_client.connect()
if not telegram_client.is_user_authorized():
    try:
        telegram_client.send_code_request(telegram_phone)
        code = input(f'Codigo de login recebio no telegram: ')
        telegram_client.sign_in(telegram_phone, code)
    except PhoneNumberBannedError:
        print(f'{telegram_phone} is banned!')
        telegram_client.disconnect()
        sys.exit(1)
    print('Authenticated')

groups = get_telegram_groups(telegram_client)
i = 0
for group in groups:
    print(f"({i}) - {group['title']}")
    i += 1 

selected_group_monitoring = groups[int(input('Selecione um grupo para monitorar: '))]
print(f"Grupo Monitorar: {selected_group_monitoring['id']}")
selected_group_redirect = groups[int(input('Selecione um grupo para redirecionar: '))]
print(f"Grupo Monitorar: {selected_group_redirect['id']}")


@telegram_client.on(events.NewMessage(chats=selected_group_monitoring['id']))
async def main(event):
    message = event.raw_text
    if 'Probabilidade de Branco' in message:
        model_1 = re.compile('[0-9]{2}:[0-9]{2} ⚪')
        correspondencias = model_1.finditer(message)
        for correspondencia in correspondencias:
            make_schedule(correspondencia.group(0))

        await telegram_client.send_message(selected_group_redirect['id'], message=f'🚨 Atenção 🚨\n<b>Entradas a caminho !!</b>\n<b>HORÁRIOS</b> : <b>{scheduler_list[0]["time"]}</b> e <b>{scheduler_list[-1]["time"]}</b>', parse_mode='html', link_preview=False)

        while True:
            if len(scheduler_list) > 0:
                for scheduler in scheduler_list:
                    if datetime.now().strftime("%H:%M") == scheduler['time']:
                        hour = scheduler['signal']
                        message = f"💰 Entrada: ⬜\n⏱Horário: {hour.replace(' ⚪', '')}\n🎲 <b>Double</b> Blaze\nCadastre-se na <b><a href='https://blaze.com/r/YwD53M'>BLAZE</a></b>"
                        await telegram_client.send_message(selected_group_redirect['id'], message, parse_mode='html', link_preview=False)
                        print(f"schedule { scheduler['signal'] } completed")
                        scheduler_list.remove(scheduler)
            else:
                break
    elif 'GREEN BRANCO!' in message:
        message = message.replace('= GREEN BRANCO! ✅', '\n✅ <b>GREEN !</b> 🚀')
        await telegram_client.send_message(selected_group_redirect['id'], message=message, parse_mode='html', link_preview=False)
    elif 'Red ❌😔' in message:
        message = message.replace('Red ❌😔', '❌ Sinais acima deram Red ❌😔')
        await telegram_client.send_message(selected_group_redirect['id'], message=message, parse_mode='html', link_preview=False)
    else:
        print(message)

telegram_client.run_until_disconnected()