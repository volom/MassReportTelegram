#!/usr/bin/env python3

import configparser
import re

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon import functions, types
from telethon import errors

import random
import time

ACCOUNTS = map(lambda x: x.replace('\n', ''), list(open("target_accounts.txt")))
ACCOUNTS = list(dict.fromkeys(ACCOUNTS))

# Enter messages for report
MESSAGES = [
    '',
    '',
    '',
    '',
    ''
]
REASONS = [
    types.InputReportReasonViolence(),
    types.InputReportReasonSpam(),
    types.InputReportReasonOther(),
    types.InputReportReasonFake(),
]
INDEXES = [ random.randrange(0, len(ACCOUNTS)) for _ in range(len(ACCOUNTS)) ]

FLOOD1 = []
FLOOD2 = []
SLEEP_SECONDS1 = 0
SLEEP_SECONDS2 = 0

# BEGIN ##############################################################################

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")

    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    while True:
        for i in INDEXES:
            try:
                result = await client(functions.messages.ReportRequest(
                    peer=ACCOUNTS[i],
                    id=[42],
                    reason=REASONS[random.randrange(0, len(REASONS))],
                    message=MESSAGES[random.randrange(0, len(MESSAGES))],
                ))
                print(f'ACCOUNT: {ACCOUNTS[i]}: Reported - {result}')

            except errors.rpcerrorlist.FloodWaitError as flood_error:
                print(f'ACCOUNT: {ACCOUNTS[i]}: Flood wait error, adding to FLOOD list')
                FLOOD1.append(ACCOUNTS[i]) # resolve for later 
                SLEEP_SECONDS1 = int(re.search(r'\d+', flood_error.__repr__()).group())

            except ValueError as value_error:
                print(f'ACCOUNT: {ACCOUNTS[i]}: Unreachable: {value_error}')

            except Exception as exception:
                print(f'ACCOUNT: {ACCOUNTS[i]}: Unhandled exception {exception} with type {type(exception)}. Please fix the code.')

        while len(FLOOD1) != 0 or len(FLOOD2) != 0:
            print(f'Sleep: {SLEEP_SECONDS1}')
            time.sleep(SLEEP_SECONDS1)

            for account in FLOOD1:
                try:
                    result = await client(functions.messages.ReportRequest(
                        peer=account,
                        id=[42],
                        reason=REASONS[random.randrange(0, len(REASONS))],
                        message=MESSAGES[random.randrange(0, len(MESSAGES))],
                    ))
                    print(f'ACCOUNT: {account}: Reported - {result}')

                except errors.rpcerrorlist.FloodWaitError as flood_error:
                    print(f'ACCOUNT: {account}: Flood wait error, adding to FLOOD list')
                    FLOOD2.append(account) # resolve for later 
                    SLEEP_SECONDS2 = int(re.search(r'\d+', flood_error.__repr__()).group())

                except ValueError as value_error:
                    print(f'ACCOUNT: {account}: Unreachable: {value_error}')

                except Exception as exception:
                    print(f'ACCOUNT: {account}: Unhandled exception {exception} with type {type(exception)}. Please fix the code.')      
            FLOOD1.clear()

            print(f'Sleep: {SLEEP_SECONDS2}')
            time.sleep(SLEEP_SECONDS2)

            for account in FLOOD2:
                try:
                    result = await client(functions.messages.ReportRequest(
                        peer=account,
                        id=[42],
                        reason=REASONS[random.randrange(0, len(REASONS))],
                        message=MESSAGES[random.randrange(0, len(MESSAGES))],
                    ))
                    print(f'ACCOUNT: {account}: Reported - {result}')

                except errors.rpcerrorlist.FloodWaitError as flood_error:
                    print(f'ACCOUNT: {account}: Flood wait error, adding to FLOOD list')
                    FLOOD1.append(account) # resolve for later 
                    SLEEP_SECONDS1 = int(re.search(r'\d+', flood_error.__repr__()).group())

                except ValueError as value_error:
                    print(f'ACCOUNT: {account}: Unreachable: {value_error}')

                except Exception as exception:
                    print(f'ACCOUNT: {account}: Unhandled exception {exception} with type {type(exception)}. Please fix the code.')      
            FLOOD2.clear()

        break # white true break

with client:
    client.loop.run_until_complete(main(phone))
