from copy import deepcopy

from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message
from database.database import user_dict_template, users_db
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book
from database.db_users import sql_start, sql_read, create_profile

router: Router = Router()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON['/help'])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)
    await sql_start()
    await create_profile(message.from_user.id)


# @router.message(CommandStart())
# async def process_start_command(message: Message):
#     if message.from_user.id not in users_db:
#         users_db[message.from_user.id] = deepcopy(user_dict_template)
#         await sql_start()
#         await create_profile(message.from_user.id)
#     await message.answer(LEXICON['/help'])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/help'])


@router.message(Command(commands='users'))
async def count_users(message: Message):
    await message.answer(f"Количество читателей: {sql_read()}")


@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    users_db[message.from_user.id]['page'] = 1
    text = book[users_db[message.from_user.id]['page']]
    await message.answer(
            text=text,
            reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[message.from_user.id]["page"]}/{len(book)}',
                    'forward'))


@router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    text = book[users_db[message.from_user.id]['page']]
    await message.answer(
                text=text,
                reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[message.from_user.id]["page"]}/{len(book)}',
                    'forward'))


# @router.message(Command(commands='bookmarks'))
# async def process_bookmarks_command(message: Message):
#     if users_db[message.from_user.id]["bookmarks"]:
#         await message.answer(
#             text=LEXICON[message.text],
#             reply_markup=create_bookmarks_keyboard(
#                 *users_db[message.from_user.id]["bookmarks"]))
#     else:
#         await message.answer(text=LEXICON['no_bookmarks'])


@router.callback_query(Text(text='forward'))
async def process_forward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] < len(book):
        users_db[callback.from_user.id]['page'] += 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                    'forward'))
    await callback.answer()


@router.callback_query(Text(text='backward'))
async def process_backward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] > 1:
        users_db[callback.from_user.id]['page'] -= 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
                text=text,
                reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                    'forward'))
    await callback.answer()


# @router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
# async def process_page_press(callback: CallbackQuery):
#     users_db[callback.from_user.id]['bookmarks'].add(
#         users_db[callback.from_user.id]['page'])
#     await callback.answer('Страница добавлена в закладки!')


@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery):
    text = book[int(callback.data)]
    users_db[callback.from_user.id]['page'] = int(callback.data)
    await callback.message.edit_text(
                text=text,
                reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                    'forward'))
    await callback.answer()


@router.callback_query(Text(text='edit_bookmarks'))
async def process_edit_press(callback: CallbackQuery):
    await callback.message.edit_text(
                text=LEXICON[callback.data],
                reply_markup=create_edit_keyboard(
                                *users_db[callback.from_user.id]["bookmarks"]))
    await callback.answer()


@router.callback_query(Text(text='cancel'))
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    users_db[callback.from_user.id]['bookmarks'].remove(
                                                    int(callback.data[:-3]))
    if users_db[callback.from_user.id]['bookmarks']:
        await callback.message.edit_text(
                    text=LEXICON['/bookmarks'],
                    reply_markup=create_edit_keyboard(
                            *users_db[callback.from_user.id]["bookmarks"]))
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()