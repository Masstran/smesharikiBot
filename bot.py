import logging
import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentTypes
from functools import reduce

# get data from config
configPath = "data/config.json"
configFile = open(configPath, "r", encoding="utf-8")
config = json.load(configFile)
configFile.close()
API_TOKEN = config["API_TOKEN"]
data_path = config["data_path"]
userlist_path = config["userlist_path"]
# list of admins (basically, just RM)
admin_user_id = config["admin_user_id"]
# chats in which the bot is used, currently not used
chat_id = config["chat_id"]
# list of stickers for П
p_sticker_ids = config["p_stickers"]
# list of stickers for РП
rp_sticker_ids = config["rp_stickers"]
# list of stickers for СП
sp_sticker_ids = config["sp_stickers"]
# list of stickers for ВП
ap_sticker_ids = config["ap_stickers"]

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_data():
    with open(data_path, "r") as data:
        return json.load(data)


def get_userlist():
    with open(userlist_path, "r") as userlistfile:
        return json.load(userlistfile)


def add_user(id, name):
    userlist = get_userlist()
    if id not in userlist:
        userlist[id] = name
        with open(userlist_path, "w") as userlistfile:
            json.dump(userlist, userlistfile, indent=4)
        return True
    return False


def check_user(message):
    user = message.from_user
    name = user.first_name + (user.last_name if user.last_name is not None else "")
    if not user.is_bot:
        add_user(user.id, name)
    if message.reply_to_message is not None:
        user = message.reply_to_message.from_user
        name = user.first_name + (user.last_name if user.last_name is not None else "")
        if not user.is_bot:
            add_user(user.id, name)


def create_markup(chatMembersWithActivatedInfo):
    keyboardMarkup = types.InlineKeyboardMarkup(row_width=3)
    rows = [[str(x[0]) if not x[1] else "!" + str(x[0]) for x in chatMembersWithActivatedInfo][x:x + 3] for x in range(0, len(chatMembersWithActivatedInfo), 3)]
    reduce(lambda x: keyboardMarkup.row(*x), rows)
    return keyboardMarkup


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Дороу, я вроде как умею считать П")


@dp.message_handler(user_id=admin_user_id, commands=['prepare'])
async def prepare_p(message: types.Message):
    # Chat members with activation sign
    chatMember = [await bot.get_chat_member(chat_id, x) for x in get_userlist()]
    chatMembersWithActivatedInfo = [(x, False) for x in chatMember if not x.user.is_bot]
    # chatMembersWithActivatedInfo = [(x, False) for x in get_userlist()]
    keyboardMarkup = create_markup(chatMembersWithActivatedInfo)
    logging.info(str(keyboardMarkup))


@dp.message_handler(content_types=ContentTypes.STICKER, user_id=admin_user_id)
async def test(message: types.Message):
    check_user(message)
    user_id = message.from_user.id
    sticker_id = message.sticker.file_unique_id
    logging.info(f"{user_id}: `{sticker_id}`")
    logging.info(type(sticker_id))
    logging.info(p_sticker_ids)
    logging.info(admin_user_id)
    logging.info(f"user_id in admin_user_id: {user_id in admin_user_id} and sticker_id in p_sticker_ids: {sticker_id in p_sticker_ids}")
    if user_id in admin_user_id and sticker_id in p_sticker_ids:
        if message.reply_to_message is None:
            await message.answer("LOL, no reply, you are a kek")
        else:
            reply_user_id = message.reply_to_message.from_user.id
            # Should add the actual count of punishment
            await message.answer(f"I guess user {reply_user_id} is getting pwned")

    elif user_id in admin_user_id and sticker_id in ap_sticker_ids:
        print("f")


# @dp.message_handler()
# async def default(message: types.Message):
#    check_user(message)

    logging.info("MESSAGE")
#    await message.answer(f"{user_id}\n`{message.sticker.sticker_id}`", parse_mode="MarkdownV2")

# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)


#chatMembersWithActivatedInfo = [(bot.get_chat_member(chat_id, x), False) for x in get_userlist() if not (bot.get_chat_member is None and bot.get_chat_member(chat_id, x).user.is_bot)]
#keyboardMarkup = create_markup(chatMembersWithActivatedInfo)
#logging.info(str(keyboardMarkup))
async def a():
    chatMember = [await bot.get_chat_member(chat_id, x) for x in get_userlist()]
    await bot.send_message(chat_id=chat_id, text=chatMember[0].user.is_bot)

import asyncio 

asyncio.run(a())
