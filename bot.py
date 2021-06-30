import logging
import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentTypes
from aiogram.utils.callback_data import CallbackData

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

callback_select_users = CallbackData("selectusers", "id", "tp")

current_active_users = {}

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_data():
    with open(data_path, "r", encoding="utf-8") as dataFile:
        json_data = json.load(dataFile)
        data = {}
        for key in json_data:
            data[int(key)] = json_data[key]
        return data


def add_data(ids, tp):
    data = get_data()
    if type(ids) is int:
        ids = [ids]
    for user_id in ids:
        if user_id not in data:
            data[user_id] = {}
            data[user_id]["P"] = 0
            data[user_id]["RP"] = 0
        data[user_id][tp] += 1
    with open(data_path, "w", encoding="utf-8") as datafile:
        json.dump(data, datafile, ensure_ascii=False, indent=4)


def get_userlist():
    with open(userlist_path, "r", encoding="utf-8") as userlistfile:
        json_userlist = json.load(userlistfile)
        userlist = {}
        for key in json_userlist:
            userlist[int(key)] = json_userlist[key]
        return userlist


def add_user(id, name):
    userlist = get_userlist()
    logging.info(userlist)
    if id not in userlist:
        userlist[id] = name
    logging.info(userlist)
    with open(userlist_path, "w", encoding="utf-8") as userlistfile:
        json.dump(userlist, userlistfile, ensure_ascii=False, indent=4)


def check_user(message):
    user = message.from_user
    name = user.first_name + ((" " + user.last_name) if user.last_name is not None else "")
    if not user.is_bot:
        add_user(user.id, name)
    if message.reply_to_message is not None:
        user = message.reply_to_message.from_user
        name = user.first_name + (" " + user.last_name if user.last_name is not None else "")
        if not user.is_bot:
            add_user(user.id, name)


def create_markup(tp):
    global current_active_users
    keyboardMarkup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=("❌ " if not current_active_users[x][1] else "✔ ") + current_active_users[x][0], callback_data=callback_select_users.new(id=x, tp=tp)) for x in current_active_users]
    keyboardMarkup.add(*buttons)
    keyboardMarkup.row(types.InlineKeyboardButton(text="Подтвердить", callback_data=callback_select_users.new(id="Confirm", tp=tp)), types.InlineKeyboardButton(text="Отменить", callback_data=callback_select_users.new(id="Cancel", tp=tp)))
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
async def detect_stickers(message: types.Message):
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
            global current_active_users
            if current_active_users == {}:
                current_active_users.clear()
                userlist = get_userlist()
                for key in userlist:
                    current_active_users[key] = [userlist[key], False]
                keyboardMarkup = create_markup("P")
                await message.answer("Select da people", reply_markup=keyboardMarkup)
            else:
                await message.answer("Some other selection is active, please finish it first")
        else:
            reply_user_id = message.reply_to_message.from_user.id
            add_data(reply_user_id, "P")
            # Should add the actual count of punishment
            await message.answer(f"I guess user {reply_user_id} is getting pwned")

    elif user_id in admin_user_id and sticker_id in ap_sticker_ids:
        print("f")


@dp.callback_query_handler(callback_select_users.filter(), user_id=admin_user_id)
async def answer_callback(call: types.CallbackQuery, callback_data: dict):
    global current_active_users
    if current_active_users == {}:
        await call.message.edit_text("Some error occured, I have no knowledge about this")
    else:
        data = callback_data["id"]
        tp = callback_data["tp"]
        if data == "Cancel":
            current_active_users = {}
            await call.message.edit_text("Canceled")
        elif data == "Confirm":
            ids = [x for x in current_active_users if current_active_users[x][1]]
            add_data(ids, tp)
            current_active_users = {}
            await call.message.edit_text("Confirmed, but nothing is yet done")
        else:
            current_active_users[int(data)][1] = not current_active_users[int(data)][1]
            keyboardMarkup = create_markup(tp)
            await call.message.edit_text("Select da people", reply_markup=keyboardMarkup)
    await call.answer()


@dp.callback_query_handler(callback_select_users.filter())
async def decline_callback(call: types.CallbackQuery, callback_data: dict):
    await call.answer(text="Не для тебя кнопка написана!!")


@dp.message_handler(commands=['test'])
async def ttt(message: types.Message):
    arguments = message.get_args()
    await message.answer(text=arguments)


@dp.message_handler(content_types=ContentTypes.ANY)
async def default(message: types.Message):
    check_user(message)

    logging.info("MESSAGE")
#    await message.answer(f"{user_id}\n`{message.sticker.sticker_id}`", parse_mode="MarkdownV2")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


# chatMembersWithActivatedInfo = [(bot.get_chat_member(chat_id, x), False) for x in get_userlist() if not (bot.get_chat_member is None and bot.get_chat_member(chat_id, x).user.is_bot)]
# keyboardMarkup = create_markup(chatMembersWithActivatedInfo)
# logging.info(str(keyboardMarkup))
# async def a():
#     chatMember = [await bot.get_chat_member(chat_id, x) for x in get_userlist()]
#     await bot.send_message(chat_id=chat_id, text=chatMember[0].user.is_bot)

# import asyncio

# asyncio.run(a())
