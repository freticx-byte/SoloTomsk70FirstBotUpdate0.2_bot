import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения ID закрепленных сообщений
pinned_messages = {}

# Константы с клавиатурами
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Информация о занятиях")],
        [KeyboardButton(text="🧑‍🏫 Творческие наставники")],
        [KeyboardButton(text="💰 Стоимость обучения")],
        [KeyboardButton(text="🎤 Записаться на пробный")],
        [KeyboardButton(text="📝 Хочу записаться на занятия")]
    ], resize_keyboard=True
)

# Все педагоги в одном списке с указанием категорий
ALL_TEACHERS = [
    {"name": "🎤 Таня Шварц (вокал)", "adult": True, "child": True},
    {"name": "🎤 Полина Шараева (вокал)", "adult": True, "child": False},
    {"name": "🎤 Катя Беркетова (вокал)", "adult": True, "child": True},
    {"name": "🎤 Вероника Тетеркина (вокал)", "adult": True, "child": False},
    {"name": "👧 Полина Романовская (детский вокал)", "adult": True, "child": True},
    {"name": "🎤 Катя Калинкина (вокал)", "adult": True, "child": True},
    {"name": "🎤 Наташа Милованова (вокал)", "adult": False, "child": True}
]

# Взрослые педагоги
ADULT_TEACHERS = [t["name"] for t in ALL_TEACHERS if t["adult"]]

# Детские педагоги
CHILD_TEACHERS = [t["name"] for t in ALL_TEACHERS if t["child"]]

# Клавиатура наставников
TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Взрослые педагоги")],
        [KeyboardButton(text="👶 Детские педагоги")],
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True
)

# Клавиатура взрослых педагогов
ADULT_TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t)] for t in ADULT_TEACHERS] + [[KeyboardButton(text="⬅️ Назад к наставникам")]],
    resize_keyboard=True
)

# Клавиатура детских педагогов
CHILD_TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t)] for t in CHILD_TEACHERS] + [[KeyboardButton(text="⬅️ Назад к наставникам")]],
    resize_keyboard=True
)

# Данные для FAQ
FAQ_ANSWERS = {
    'faq_1': "💵 **Стоимость занятий:**\n\n• Индивидуальный пробный урок - 900 руб.\n• Пробный урок в группе - 850 руб.\n\n📞 По вопросам обращайтесь: +7-(913)-856-93-10",
    'faq_2': "⏰ **Расписание:**\n\n• Групповые занятия - после работы по будням\n• Индивидуальные уроки - по договоренности\n\n📞 Уточните расписание у администратора: +7-(913)-856-93-10",
    'faq_3': "📅 **Регулярность занятий:**\n\n• Для новичков: 3 раза в неделю\n• Для опытных: 2 раза в месяц\n• Минимальный курс: 3 месяца",
    'faq_4': "🎓 **О педагогах:**\n\n• Концертный опыт от 8 лет\n• Музыкальное образование\n• Лауреаты конкурсов\n• Любовь к музыке и саморазвитию",
    'faq_5': "📚 **Структура урока:**\n\n1️⃣ Определение целей\n2️⃣ Разминка и дыхание\n3️⃣ Вокальные упражнения\n4️⃣ Работа с репертуаром",
    'faq_6': "👶👵 **Возраст:**\n\n• От 3 до 50+ лет\n• В любом возрасте можно развить голос"
}

# Данные для комнат
ROOMS_DATA = [
    ("miniroom",
     "🎤 **Зал 1: Малый**\n\n✅ Уютный зал с зеркалом\n✅ Электронное пианино\n✅ Вокальная стойка\n✅ Wi-Fi\n\nИдеально для записи вокала и сольных репетиций."),
    ("midleroom",
     "🎸 **Зал 2: Средний**\n\n✅ Телевизор для презентаций\n✅ Колонка-монитор\n✅ Микрофоны и стойка\n✅ Стулья\n✅ Wi-Fi\n\nОтлично подходит для групповых занятий."),
    ("bigroom",
     "🎧 **Зал 3: Большой**\n\n✅ Сцена\n✅ Колонка-монитор\n✅ Беспроводной микрофон\n✅ Стойка\n✅ Дополнительные стулья\n✅ Wi-Fi\n\nДля подготовки к выступлениям.")
]

# Данные для дипломов
TANIA_DIPLOMS = [
    ("🎓 IATS", "IATS"),
    ("🎓 BIOPHONICS", "BIOPHONICS"),
    ("🎓 Light Voice", "Light Voice"),
    ("🎓 Профессиональное образование", "Профессиональное образование"),
    ("🎓 Estil Voice", "Estil Voice")
]

POLINA_DIPLOMS = [
    ("🎓 ESTIL VOICE", "🎓 **ESTIL VOICE**", "1.png"),
    ("🎓 DIVA VOICE", "🎓 **DIVA VOICE**", "2.png")
]

last_faq_messages = {}

# ID администратора для получения уведомлений
ADMIN_ID = 1736644499


# Класс для хранения состояний анкеты
class LessonForm(StatesGroup):
    subject = State()
    name = State()
    contact = State()
    who = State()
    experience_vocal = State()
    experience_instrument = State()
    goal = State()
    time = State()
    source = State()


async def send_welcome(message: types.Message):
    """Отправляет приветствие с фото"""
    welcome_text = f"👋 Привет, {message.from_user.first_name}!\nЯ бот-помощник студии **solo** 🎙️\nВыберите интересующий вас раздел:"
    try:
        await message.answer_photo(photo=FSInputFile("solo.png"), caption=welcome_text)
    except:
        await message.answer(welcome_text)


async def send_inline_buttons(message: types.Message):
    """Отправляет инлайн-кнопки и закрепляет сообщение"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq_menu"),
        InlineKeyboardButton(text="⭐ Отзывы", callback_data="reviews"),
        InlineKeyboardButton(text="🏠 Наши залы", callback_data="rooms"),
        InlineKeyboardButton(text="🌐 Сайт | Telegram", callback_data="site"),
        InlineKeyboardButton(text="📍 Где мы находимся?", callback_data="ourplace"),
        InlineKeyboardButton(text="🤫 Анонимный вопрос", callback_data="anonimquestion"), width=2
    )
    sent_msg = await message.answer("🔽 **Полезные ссылки:**", reply_markup=builder.as_markup())

    # Закрепляем сообщение
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
        pinned_messages[message.chat.id] = sent_msg.message_id
    except Exception as e:
        print(f"Ошибка закрепления сообщения: {e}")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await send_welcome(message)

    # Отправляем бонус
    try:
        bonus_text = "🎁 **Вступайте в наш телеграм канал, получите занятия в подарок или с хорошей скидкой** ✌️🎶\n\nhttps://t.me/+EMU-EPeAfwlkYTFi"
        await message.answer_photo(photo=FSInputFile("bonus.png"), caption=bonus_text)
    except:
        bonus_text = "🎁 **Вступайте в наш телеграм канал, получите занятия в подарок или с хорошей скидкой** ✌️🎶\n\nhttps://t.me/+EMU-EPeAfwlkYTFi"
        await message.answer(bonus_text)

    await send_inline_buttons(message)
    await message.answer("📋 **Основное меню:**", reply_markup=MAIN_KEYBOARD)


# ==================== СИСТЕМА ЗАПИСИ ====================

@dp.message(F.text == "🎤 Записаться на пробный")
async def start_trial_form(message: types.Message, state: FSMContext):
    await state.set_state(LessonForm.subject)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎤 Вокал")],
            [KeyboardButton(text="🎸 Гитара")],
            [KeyboardButton(text="🪕 Укулеле")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "🎯 **Выберите предмет:**\n\n"
        "Чем хотите заниматься?",
        reply_markup=kb
    )


@dp.message(F.text == "📝 Хочу записаться на занятия")
async def start_enroll_form(message: types.Message, state: FSMContext):
    await state.set_state(LessonForm.subject)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎤 Вокал")],
            [KeyboardButton(text="🎸 Гитара")],
            [KeyboardButton(text="🪕 Укулеле")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "🎯 **Выберите предмет:**\n\n"
        "Чем хотите заниматься?",
        reply_markup=kb
    )


@dp.message(LessonForm.subject)
async def process_subject(message: types.Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)
    await state.set_state(LessonForm.name)
    await message.answer("📝 **Введите ваше имя:**")


@dp.message(LessonForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(LessonForm.contact)
    await message.answer("📞 **Введите телефон или Telegram для связи:**")


@dp.message(LessonForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(LessonForm.who)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👶 Ребёнок (5-11)")],
            [KeyboardButton(text="🧑 Подросток(11-18)")],
            [KeyboardButton(text="👨 Взрослый(18+)")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("👥 **Кто будет заниматься?**", reply_markup=kb)


@dp.message(LessonForm.who)
async def process_who(message: types.Message, state: FSMContext):
    who = message.text
    await state.update_data(who=who)

    data = await state.get_data()
    subject = data.get('subject', '')

    if "Вокал" in subject:
        await state.set_state(LessonForm.experience_vocal)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="❌ Никогда")],
                [KeyboardButton(text="🎤 Немного для себя")],
                [KeyboardButton(text="📚 Занимался(ась)")],
                [KeyboardButton(text="🎭 Профессионально")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("🎵 **Пробовали петь раньше?**", reply_markup=kb)
    else:
        await state.set_state(LessonForm.experience_instrument)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="❌ Начинаю с нуля")],
                [KeyboardButton(text="🎸 Немного играл(а)")],
                [KeyboardButton(text="📚 Занимался(ась)")],
                [KeyboardButton(text="🎭 Профессионально")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("🎸 **Играли на инструменте раньше?**", reply_markup=kb)


@dp.message(LessonForm.experience_vocal)
async def process_experience_vocal(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)

    # Получаем данные о том, кто будет заниматься
    data = await state.get_data()
    who = data.get('who', '')

    # Вызываем ask_goal с параметром who
    await ask_goal(message, state, who)


@dp.message(LessonForm.experience_instrument)
async def process_experience_instrument(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)

    # Получаем данные о том, кто будет заниматься
    data = await state.get_data()
    who = data.get('who', '')

    # Вызываем ask_goal с параметром who
    await ask_goal(message, state, who)


async def ask_goal(message: types.Message, state: FSMContext, who: str):
    await state.set_state(LessonForm.goal)

    # Базовая клавиатура для всех
    base_keyboard = [
        [KeyboardButton(text="🎤 Петь/играть для себя")],
        [KeyboardButton(text="🎭 Подготовиться к выступлению")],
        [KeyboardButton(text="💼 Развить навыки для работы")],
    ]

    # Добавляем кнопку для детей, если это ребенок
    if "Ребёнок" in who:
        base_keyboard.append([KeyboardButton(text="👶 Ребёнку для развития")])

    # Добавляем кнопку "Другое" для всех
    base_keyboard.append([KeyboardButton(text="📝 Другое")])

    kb = ReplyKeyboardMarkup(
        keyboard=base_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🎯 **Что хотите получить от занятий?**", reply_markup=kb)


@dp.message(LessonForm.goal)
async def process_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(LessonForm.time)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌅 Утро")],
            [KeyboardButton(text="☀️ День")],
            [KeyboardButton(text="🌙 Вечер")],
            [KeyboardButton(text="🤔 Любое, нужен совет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("⏰ **Удобное время для занятий:**", reply_markup=kb)


@dp.message(LessonForm.time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(LessonForm.source)
    await message.answer("🔍 **Откуда вы о нас узнали?** (напишите в свободной форме)")


@dp.message(LessonForm.source)
async def process_source(message: types.Message, state: FSMContext):
    await state.update_data(source=message.text)

    data = await state.get_data()

    # Формируем сообщение для администратора
    admin_message = (
        f"📝 **НОВАЯ ЗАЯВКА!**\n\n"
        f"🎯 **Предмет:** {data.get('subject', 'Не указан')}\n"
        f"👤 **Имя:** {data.get('name', 'Не указано')}\n"
        f"📞 **Контакт:** {data.get('contact', 'Не указан')}\n"
        f"👥 **Кто будет заниматься:** {data.get('who', 'Не указано')}\n"
        f"📊 **Опыт:** {data.get('experience', 'Не указан')}\n"
        f"🎯 **Цель:** {data.get('goal', 'Не указана')}\n"
        f"⏰ **Удобное время:** {data.get('time', 'Не указано')}\n"
        f"🔍 **Откуда узнали:** {data.get('source', 'Не указано')}\n"
        f"🆔 **ID пользователя:** {message.from_user.id}\n"
        f"📱 **Username:** @{message.from_user.username if message.from_user.username else 'нет'}"
    )

    # Отправляем администратору
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_message)
        await message.answer(
            "✅ **Спасибо! Ваша заявка отправлена.**\n\n"
            "Мы свяжемся с вами в ближайшее время, чтобы подобрать удобное время и педагога. "
            "Без спама, только по делу 🧡",
            reply_markup=MAIN_KEYBOARD
        )
    except Exception as e:
        await message.answer(
            "❌ **Ошибка отправки заявки.**\n\n"
            "Пожалуйста, свяжитесь с нами напрямую по телефону: +7-(913)-856-93-10",
            reply_markup=MAIN_KEYBOARD
        )
        print(f"Ошибка отправки админу: {e}")

    await state.clear()


# ==================== ОБРАБОТЧИКИ КНОПОК ====================

@dp.callback_query(lambda c: c.data == "reviews")
async def process_reviews_callback(c: CallbackQuery):
    await c.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Перейти в канал с отзывами", url="https://t.me/solo70_reviews")]])
    await c.message.answer("👥 **Наш канал с отзывами:**", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "anonimquestion")
async def process_anonimquestion_callback(c: CallbackQuery):
    await c.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤫 Задать анонимный вопрос", url="t.me/anonaskbot?start=kpsgjhclry2zs97u")]])
    await c.message.answer("📱 **Нажмите кнопку ниже чтобы задать анонимный вопрос:**", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "faq_menu")
async def process_faq_menu_callback(c: CallbackQuery):
    await c.answer()
    builder = InlineKeyboardBuilder()
    faq_buttons = [
        ("💰 Стоимость", "faq_1"),
        ("⏰ Расписание", "faq_2"),
        ("📅 Регулярность", "faq_3"),
        ("🎓 Педагоги", "faq_4"),
        ("📚 Структура урока", "faq_5"),
        ("👶👵 Возраст", "faq_6")
    ]
    for i in range(0, len(faq_buttons), 2):
        builder.row(
            InlineKeyboardButton(text=faq_buttons[i][0], callback_data=faq_buttons[i][1]),
            InlineKeyboardButton(text=faq_buttons[i + 1][0], callback_data=faq_buttons[i + 1][1]), width=2
        )
    await c.message.answer("❓ **Выберите вопрос:**", reply_markup=builder.as_markup())


@dp.callback_query(lambda c: c.data == "ourplace")
async def process_ourplace_callback(c: CallbackQuery):
    await c.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📍 2ГИС", url="https://2gis.ru/tomsk/geo/422848120231246"),
            InlineKeyboardButton(text="🗺️ Яндекс Карты",
                                 url="https://yandex.ru/maps/67/tomsk/house/ulitsa_nikitina_8a/bE0YfwJpTUwPQFtsfXh2dnVmZA==/?ll=84.959497%2C56.477950&z=17")
        ]
    ])
    await c.message.answer("📍 **Мы на картах:**", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "site")
async def process_site_callback(c: CallbackQuery):
    await c.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 Наш сайт", url="https://solotomsk.ru"),
            InlineKeyboardButton(text="📱 Telegram канал", url="https://t.me/+EMU-EPeAfwlkYTFi")
        ]
    ])
    await c.message.answer("🔗 **Полезные ссылки:**", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data and c.data.startswith('faq_') and c.data != "faq_menu")
async def process_faq_callback(c: CallbackQuery):
    await c.answer()
    user_id = c.from_user.id
    if user_id in last_faq_messages:
        try:
            await bot.delete_message(chat_id=c.message.chat.id, message_id=last_faq_messages[user_id])
        except:
            pass
    sent_message = await c.message.answer(FAQ_ANSWERS.get(c.data, "❌ Ответ не найден"))
    last_faq_messages[user_id] = sent_message.message_id


@dp.callback_query(lambda c: c.data == "rooms")
async def process_rooms_callback(c: CallbackQuery):
    await c.answer()
    for i, (room, text) in enumerate(ROOMS_DATA, 1):
        try:
            await c.message.answer_photo(photo=FSInputFile(f"rooms/{room}/room{i}.1.png"), caption=text)
        except:
            await c.message.answer(f"Фото зала {i} (1) не найдено")
        try:
            await c.message.answer_photo(photo=FSInputFile(f"rooms/{room}/room{i}.2.png"),
                                         caption=f"{'🎤' if i == 1 else '🎸' if i == 2 else '🎧'} Зал {i} - дополнительный ракурс")
        except:
            await c.message.answer(f"Фото зала {i} (2) не найдено")


@dp.message(F.text == "📄 Информация о занятиях")
async def info_lessons(message: types.Message):
    await message.answer(
        "📚 **Структура урока по вокалу:**\n\n"
        "1️⃣ Определение целей и способностей ученика\n"
        "2️⃣ Разминка и тренировка дыхания\n"
        "3️⃣ Упражнения для голоса\n"
        "4️⃣ Работа с репертуаром\n"
        "5️⃣ Подготовка к выступлению"
    )


@dp.message(F.text == "🧑‍🏫 Творческие наставники")
async def info_teachers(message: types.Message):
    await message.answer("👥 **Выберите категорию педагогов:**", reply_markup=TEACHERS_KEYBOARD)


@dp.message(F.text == "👥 Взрослые педагоги")
async def adult_teachers(message: types.Message):
    await message.answer("👥 **Взрослые педагоги:**", reply_markup=ADULT_TEACHERS_KEYBOARD)


@dp.message(F.text == "👶 Детские педагоги")
async def child_teachers(message: types.Message):
    await message.answer("👶 **Детские педагоги:**", reply_markup=CHILD_TEACHERS_KEYBOARD)


# ==================== ОБРАБОТЧИКИ ПЕДАГОГОВ ====================

@dp.message(F.text == "🎤 Таня Шварц (вокал)")
async def teacher_taniaswarz(message: types.Message):
    desc = ("👩‍🏫 **Таня Шварц**\n\n"
            "⭐ Опыт работы: 10 лет\n\n"
            "🎯 Помогу:\n"
            "• Поставить голос\n"
            "• Записать свою песню\n"
            "• Подготовиться к выступлению\n\n"
            "📚 **Образование:**\n"
            "• Колледж имени Эдисона, ТПУ\n"
            "• Курсы методики EVT (Италия)")
    try:
        await message.answer_photo(photo=FSInputFile("Diplom Tania Swarz/Tania.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t, _ in TANIA_DIPLOMS] + [
            [KeyboardButton(text="⬅️ Назад к наставникам")]],
        resize_keyboard=True
    )
    await message.answer("📜 **Дипломы и сертификаты:**", reply_markup=kb)


# Дипломы Тани
for idx, (text, caption) in enumerate(TANIA_DIPLOMS, 1):
    @dp.message(F.text == text)
    async def diploma_handler(message: types.Message, i=idx, cap=caption):
        try:
            if i == 1:
                path = "Diplom Tania Swarz/diplom 1.1.png"
            else:
                path = f"Diplom Tania Swarz/diplom 1.{i}.png"
            await message.answer_photo(photo=FSInputFile(path), caption=f"📜 {cap}")
        except Exception as e:
            await message.answer(f"❌ Фото диплома {i} не найдено")


@dp.message(F.text == "🎤 Полина Шараева (вокал)")
async def teacher_polina_sharaeva(message: types.Message):
    desc = ("👩‍🏫 **Полина Шараева**\n\n"
            "⭐ Опыт работы: 10 лет\n\n"
            "🎯 Джазовая певица, резидент @jazzcafeunderground\n"
            "Работает с известными джазовыми музыкантами\n\n"
            "📚 **Образование:**\n"
            "• Курс Ольги Кляйн 2023\n"
            "• DIVA International 2024\n"
            "• Estill Voice training 2023")
    try:
        await message.answer_photo(photo=FSInputFile("PolinaSharaeva/PolinaSharaews.jpg"), caption=desc)
    except Exception as e:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t, _, _ in POLINA_DIPLOMS] + [
            [KeyboardButton(text="⬅️ Назад к наставникам")]],
        resize_keyboard=True
    )
    await message.answer("📜 **Дипломы и сертификаты:**", reply_markup=kb)


# Дипломы Полины Шараевой
for text, caption, filename in POLINA_DIPLOMS:
    @dp.message(F.text == text)
    async def diploma_polina_handler(message: types.Message, fname=filename, cap=caption):
        try:
            await message.answer_photo(photo=FSInputFile(f"PolinaSharaeva/diploms/{fname}"), caption=cap)
        except Exception as e:
            await message.answer("❌ Фото диплома не найдено")


@dp.message(F.text == "🎤 Вероника Тетеркина (вокал)")
async def teacher_nika_teterkina(message: types.Message):
    desc = ("👩‍🏫 **Вероника Тетеркина**\n\n"
            "🎯 Педагог по вокалу, вокалотерапевт\n"
            "• Работала в Германии\n"
            "• Особенный подход к каждому\n\n"
            "📚 ГСКТИИ, курс Ольги Кляйн\n\n"
            "⭐ Опыт: 8 лет")
    try:
        await message.answer_photo(photo=FSInputFile("NikaTeterkina/NikaTeterkina.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Салют талантов")],
            [KeyboardButton(text="🎓 Estill Voice")],
            [KeyboardButton(text="⬅️ Назад к наставникам")]
        ],
        resize_keyboard=True
    )
    await message.answer("📜 **Дипломы и сертификаты:**", reply_markup=kb)


@dp.message(F.text == "🎤 Катя Беркетова (вокал)")
async def teacher_katya_berketova(message: types.Message):
    desc = ("👩‍🏫 **Катя Беркетова**\n\n"
            "🏆 Победитель конкурсов в Москве, СПб, Казани\n"
            "📺 Участник «Универвидение» на MTV\n"
            "✍️ Автор вокальных интенсивов\n\n"
            "📚 **Образование:**\n"
            "• ГКСКТИИ\n"
            "• СПбГИК (магистр)\n\n"
            "⭐ Опыт: 9 лет")
    try:
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/KatyaBerketova.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Диплом ГКСКТИИ")],
            [KeyboardButton(text="🎓 Диплом СПбГИК")],
            [KeyboardButton(text="🏆 Дипломы конкурсов")],
            [KeyboardButton(text="⬅️ Назад к наставникам")]
        ],
        resize_keyboard=True
    )
    await message.answer("📜 **Дипломы Кати Беркетовой:**", reply_markup=kb)


@dp.message(F.text == "👧 Полина Романовская (детский вокал)")
async def teacher_polina_romanovskaya(message: types.Message):
    desc = ("👩‍🏫 **Полина Романовская**\n\n"
            "🎯 Детский педагог студии «Соло дети»\n"
            "• Дипломированный специалист\n"
            "• Лауреат конкурсов\n"
            "• Вокалистка группы «Tres Jolie»\n\n"
            "⭐ Опыт: более 3 лет")
    try:
        await message.answer_photo(photo=FSInputFile("PolinaRomanovskaya/SOLO01275.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Дипломы")],
            [KeyboardButton(text="⬅️ Назад к наставникам")]
        ],
        resize_keyboard=True
    )
    await message.answer("📜 **Достижения Полины Романовской:**", reply_markup=kb)


@dp.message(F.text == "🎤 Катя Калинкина (вокал)")
async def teacher_katya_kalinkina(message: types.Message):
    desc = ("👩‍🏫 **Катя Калинкина**\n\n"
            "🎯 Работает с дошкольниками и подростками\n"
            "• Руководитель коллектива «Мармеладки»\n"
            "• Победитель «Педагогический дебют» 2015\n\n"
            "📚 ТПУ, ТГПУ")
    try:
        await message.answer_photo(photo=FSInputFile("KatyaKalinkina/KatyaKalinkina.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Дипломы")],
            [KeyboardButton(text="⬅️ Назад к наставникам")]
        ],
        resize_keyboard=True
    )
    await message.answer("📜 **Достижения Кати Калинкиной:**", reply_markup=kb)


@dp.message(F.text == "🎤 Наташа Милованова (вокал)")
async def teacher_natasha_milovanova(message: types.Message):
    desc = ("👩‍🏫 **Наташа Милованова**\n\n"
            "🎯 Руководитель детских вокальных групп\n"
            "• Педагог высшей категории\n"
            "• Лауреат конкурсов\n\n"
            "📚 Колледж имени Эдисона Денисова\n\n"
            "⭐ Опыт: 6 лет")
    try:
        await message.answer_photo(photo=FSInputFile("NatashaMilovanova/NatashaMilovanova.jpg"), caption=desc)
    except:
        await message.answer(desc)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Дипломы")],
            [KeyboardButton(text="⬅️ Назад к наставникам")]
        ],
        resize_keyboard=True
    )
    await message.answer("📜 **Достижения Наташи Миловановой:**", reply_markup=kb)


# Дипломы для детских педагогов
@dp.message(F.text == "📜 Дипломы")
async def diplomas_child_teachers(message: types.Message):
    await message.answer("📜 **Дипломы и сертификаты пока в разработке. Скоро добавлю! 🎓✨")


# Дипломы Вероники Тетеркиной
@dp.message(F.text == "🎓 Салют талантов")
async def diploma_nika_t1(message: types.Message):
    try:
        await message.answer_photo(photo=FSInputFile("NikaTeterkina/1.png"), caption="🏆 **Салют талантов**")
    except:
        await message.answer("❌ Фото диплома не найдено")


@dp.message(F.text == "🎓 Estill Voice")
async def diploma_nika_t2(message: types.Message):
    try:
        await message.answer_photo(photo=FSInputFile("NikaTeterkina/2.png"), caption="🎓 **Estill Voice**")
    except:
        await message.answer("❌ Фото диплома не найдено")


# Дипломы Кати Беркетовой
@dp.message(F.text == "🎓 Диплом ГКСКТИИ")
async def diploma_katya_b1(message: types.Message):
    try:
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_gksktii.jpg"),
                                   caption="🎓 ГКСКТИИ")
    except:
        await message.answer("❌ Фото диплома не найдено")


@dp.message(F.text == "🎓 Диплом СПбГИК")
async def diploma_katya_b2(message: types.Message):
    try:
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_spbgik.jpg"),
                                   caption="🎓 СПбГИК, Магистр")
    except:
        await message.answer("❌ Фото диплома не найдено")


@dp.message(F.text == "🏆 Дипломы конкурсов")
async def diploma_katya_b3(message: types.Message):
    try:
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_konkursy.jpg"),
                                   caption="🏆 Дипломы конкурсов")
    except:
        await message.answer("❌ Фото диплома не найдено")


# Обработчики навигации
@dp.message(F.text == "⬅️ Назад к наставникам")
async def back_to_teachers_menu(message: types.Message):
    await message.answer("👥 **Выберите категорию педагогов:**", reply_markup=TEACHERS_KEYBOARD)


@dp.message(F.text == "⬅️ Назад")
async def back_to_main_from_anywhere(message: types.Message):
    await send_welcome(message)
    await send_inline_buttons(message)
    await message.answer("📋 **Основное меню:**", reply_markup=MAIN_KEYBOARD)


@dp.message(F.text == "💰 Стоимость обучения")
async def info_price(message: types.Message):
    await message.answer("💵 **Расценки на обучение:**\n\n⏳ Загружаю актуальные цены...")

    # Первое фото с ценами на инструменты
    try:
        photo1 = FSInputFile("Price tags/raszenci1.jpg")
        caption1 = (
            "🎹 **Фортепиано**\n"
            "• Абонемент: 6000 руб/мес (4 занятия) — 1500 руб/занятие\n"
            "• Разовое занятие: 1900 руб\n"
            "Только индивидуально\n\n"
            "🎸 **Гитара / Укулеле**\n"
            "• Абонемент: 6000 руб/мес (4 занятия) — 1500 руб/занятие\n"
            "• Разовое занятие: 1900 руб\n"
            "Только индивидуально\n\n"
            "👥 **Мини-группа (2 человека)**\n"
            "• 3600 руб/мес (900 руб/занятие)\n\n"
            "⏱️ Продолжительность занятия — 55 минут\n\n"
            "🎵 В результате занятий вы научитесь практическим навыкам игры на инструменте "
            "и познакомитесь с азами музыкальной теории."
        )
        await message.answer_photo(photo=photo1, caption=caption1)
    except Exception as e:
        print(f"Ошибка загрузки raszenci1.jpg: {e}")
        await message.answer("❌ Ошибка загрузки изображения 1")

    # Второе фото с ценами на групповые занятия
    try:
        photo2 = FSInputFile("Price tags/raszenci2.jpg")
        caption2 = (
            "🎵 **Групповые занятия**\n\n"
            "🎤 **Хор для взрослых** (среда, 19:00)\n"
            "• 300 руб/занятие\n\n"
            "👥 **Группа для подростков** (вторник, четверг)\n"
            "• 6100 руб/мес (12 занятий)\n\n"
            "👶 **Группа для малышей 4-5 лет** (вторник, четверг, 19:00)\n"
            "• 4100 руб/мес (8 занятий)\n\n"
            "🎷 **Джазовый ансамбль с Анастасией Сатаровой**\n"
            "• Для взрослых, понедельник 19:00\n"
            "• 5600 руб/мес (8 занятий по 45 мин)\n\n"
            "🏠 **Аренда зала**\n"
            "• Для учеников: 700 руб/час\n"
            "• Для гостей студии: от 1100 руб/час\n"
            "*(точная стоимость зависит от количества человек и формата мероприятия)*"
        )
        await message.answer_photo(photo=photo2, caption=caption2)
    except Exception as e:
        print(f"Ошибка загрузки raszenci2.jpg: {e}")
        await message.answer("❌ Ошибка загрузки изображения 2")

    # Третье фото (если есть)
    try:
        photo3 = FSInputFile("Price tags/raszenci3.jpg")
        await message.answer_photo(photo=photo3)
    except Exception as e:
        print(f"Ошибка загрузки raszenci3.jpg: {e}")
        pass


async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
