import random
from aiogram import Router
from aiogram.types import Message
from services.file_handling import book
from database.database import users_db
from keyboards.pagination_kb import create_pagination_keyboard
import logging

router: Router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def send_echo(message: Message):
    pages = ['/page_0', '/page_1', '/page_2', '/page_3', '/page_4', '/page_5', '/page_6', '/page_7', '/page_8', '/page_9',
             '/page_10', '/page_11', '/page_12', '/page_13', '/page_14', '/page_15', '/page_16', '/page_17', '/page_18',
             '/page_19', '/page_20', '/page_21', '/page_22', '/page_23', '/page_24', '/page_25', '/page_26', '/page_27',
             '/page_28', '/page_29', '/page_30', '/page_31', '/page_32']
    random_index = random.randint(1, len(pages))

    if message.text not in pages:
        users_db[message.from_user.id]['page'] = random_index
        text = book[users_db[message.from_user.id]['page']]
        await message.answer(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[message.from_user.id]["page"]}/{len(book)}',
                'forward'))
    else:
        users_db[message.from_user.id]['page'] = int(message.text[6:])
        text = book[users_db[message.from_user.id]['page']]
        await message.answer(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[message.from_user.id]["page"]}/{len(book)}',
                'forward'))
