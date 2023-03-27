from aiogram import Bot, Dispatcher, F
import requests
from aiogram.filters import Text, Command, CommandStart, BaseFilter
from aiogram.types import Message
from random import randint
from testing import isAdmin

print(__name__)

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
API_TOKEN: str = '6243871881:AAEEoo5zKY5ekyrwllLXAoBw4H3mIh7emK8'
API_CATS_URL: str = 'https://aws.random.cat/meow'

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

cat_response: requests.Response
cat_link: str

#..................
admin_ids: list[int] = [5782841374]

#class isAdmin(BaseFilter):
#    def __init__(self, admin_ids: list[int]) -> None:
#        self.admin_ids = admin_ids

#    async def __call__(self, message: Message) -> bool:
#        return message.from_user.id in self.admin_ids
#..................
#фильтр на числа=======================================

@dp.message(isAdmin(admin_ids))
async def process_if_you_admin(message: Message):
    await message.answer('Вы админ')

class NumbersInMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        numbers = []
        for word in message.text.split():
            normalized_word = word.replace('.', '').replace(',', '').strip()
            if normalized_word.isdigit():
                numbers.append(int(normalized_word))
        if numbers:
            return {'numbers': numbers}
        return False


@dp.message(Text(startswith='Найди числа', ignore_case=True), NumbersInMessage())


async def process_if_numbers(message: Message, numbers: list[int]):
    await message.answer(text=f'Нашёл: {str(", ".join(str(num) for num in numbers))}')


@dp.message(Text(startswith='Найди числа', ignore_case=True))


async def process_if_not_numbers(message: Message):
    await message.answer(text='Что то не нашёл')

@dp.message(lambda x: any([x.photo, x.voice]))

async def photo_or_voice(message: Message):
    await message.answer('Вы прислали фото или голосовое сообщение')

#игра угадай число=================================================================================


attempts: int = 5

users: dict = {}


def get_random() -> int:
    return randint(1, 100)

def filter_start(message: Message) -> bool:
    return message.text == '/start'

#@dp.message(isAdmin(admin_ids))
#async def answer_if_admis_update(message: Message):
#    await message.answer(text='Ты админ')

@dp.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer('Привет\nДавай сыграем в игру "Угадай число"?\n\n'
                         'Чтобы получить правила игры и список доступных'
                          ' команд - отправьте команду /help')
    if message.from_user.id not in users:
        users[message.from_user.id] = {'in_game': False,
                                       'secret_number': None,
                                       'attempts': None,
                                       'total_games': 0,
                                       'wins': 0}

@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                         f'а вам нужно его угадать\nУ вас есть {attempts} '
                         f'попыток\n\nДоступные команды:\n/help - правила '
                         f'игры и список команд\n/cancel - выйти из игры\n'
                         f'/stat - посмотреть статистику\n\nДавай сыграем?')

@dp.message(Command(commands=['stat']))
async def process_stat_command(message: Message):
    await message.answer(f'Всего сыграно игр {users[message.from_user.id]["total_games"]}\n'
                         f'Игр выиграно {users[message.from_user.id]["wins"]}')

@dp.message(Command(commands=['cancel']))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Вы вышли из игры. Если хотите сыграть снова - напишите об этом')
        users[message.from_user.id]['in_game'] = False
    else:
        await message.answer('А мы итак с вами не играем. Может сыграем разок?')

@dp.message(Text(text=["Да", "Давай", "Хочу играть", "Сыграем", "Игра", "Играть"], ignore_case=True))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Ура!\n\nЯ загадал число от 1 до 100, попробуй угадать!')
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = get_random()
        users[message.from_user.id]['attempts'] = attempts
    else:
        await message.answer('Пока мы играем в игру я могу реагировать только на числа от 1 до 100 '
                             'и команды /cancel и /stat')

@dp.message(Text(text=["Не", "Нет", " Не хочу", "Не буду"], ignore_case=True))
async def process_negative_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Жаль :)\n\nЕсли хотите поиграть - просто напишите об этом')
    else:
        await message.answer('Мы же сейчас с вами играем. Присылайте пожалуйста числа от 1 до 100')

@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_number_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            await message.answer('Ура!Вы угадали число!\n\nМожет сыграем ещё раз?')
            cat_response = requests.get(API_CATS_URL)
            if cat_response.status_code == 200:
                cat_link = cat_response.json()['file']
                await message.answer_photo(cat_link)
            users[message.from_user.id]['in_game']=False
            users[message.from_user.id]['total_games']+=1
            users[message.from_user.id]['wins']+=1
        elif int(message.text)>users[message.from_user.id]['secret_number']:
            await message.answer('Моё число меньше')
            users[message.from_user.id]['attempts']-=1
        elif int(message.text)<users[message.from_user.id]['secret_number']:
            await message.answer('Моё число больше')
            users[message.from_user.id]['attempts']-=1

        if users[message.from_user.id]['attempts']==0:
            await message.answer(f'К сожалению у вас больше не осталось попыток. '
                         f'Вы проиграли :(\n\Моё число было {users[message.from_user.id]["secret_number"]}\n\n'
                         f'Давайте сыграем ещё? ')
            users[message.from_user.id]['in_game']=False
            users[message.from_user.id]['total_games']+=1
    else:
        await message.answer('Мы ещё не играем. Хотите сыграть?')

@dp.message()
async def other_text_message(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Мы же сейчас с вами играем. Присылайте пожалуйста числа от 1 до 100')
    else:
        cat_response = requests.get(API_CATS_URL)
        if cat_response.status_code == 200:
                cat_link = cat_response.json()['file']
                await message.answer('Я довольно ограниченный бот, могу показать котика=)\n'
                                    'Нажмите /start чтобы начать')
                await message.answer_photo(cat_link)

#==================================================================================================


if __name__ == '__main__':
    dp.run_polling(bot)