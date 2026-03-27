import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

bot = Bot(token="8778398187:AAF6IsW4J7ZSB5TiLAoALU3g1clsxvxR2ZA")
dp = Dispatcher(storage=MemoryStorage())

pinned_messages = {}

# ПОЛЕЗНЫЕ ССЫЛКИ (reply-кнопки)
USEFUL_LINKS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Частые вопросы")],
        [KeyboardButton(text="⭐ Отзывы")],
        [KeyboardButton(text="🏠 Наши залы")],
        [KeyboardButton(text="🌐 Сайт | Telegram")],
        [KeyboardButton(text="📍 Где мы находимся?")],
        [KeyboardButton(text="🤫 Анонимный вопрос")]
    ], resize_keyboard=True
)

# ОСНОВНОЕ МЕНЮ (инлайн-кнопки)
async def send_main_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 Информация о занятиях", callback_data="info_lessons"),
        InlineKeyboardButton(text="🧑‍🏫 Творческие наставники", callback_data="info_teachers"),
        width=2
    )
    builder.row(
        InlineKeyboardButton(text="💰 Стоимость обучения", callback_data="info_price"),
        InlineKeyboardButton(text="🎤 Записаться на пробный", callback_data="start_trial"),
        width=2
    )
    builder.row(
        InlineKeyboardButton(text="📝 Хочу записаться на занятия", callback_data="start_enroll"),
        width=1
    )
    sent_msg = await message.answer("📋 Основное меню:", reply_markup=builder.as_markup())
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
        pinned_messages[message.chat.id] = sent_msg.message_id
    except:
        pass


# ВСЕ ПЕДАГОГИ
ALL_TEACHERS = [
    {"name": "🎤 Таня Шварц (вокал)", "adult": True, "child": True, "photo": "Diplom Tania Swarz/Tania.jpg", "desc": "Таня Шварц"},
    {"name": "🎤 Полина Шараева (вокал)", "adult": True, "child": False, "photo": "PolinaSharaeva/PolinaSharaews.jpg", "desc": "Полина Шараева"},
    {"name": "🎤 Катя Беркетова (вокал)", "adult": True, "child": True, "photo": "KatyaBerketova/KatyaBerketova.jpg", "desc": "Катя Беркетова"},
    {"name": "🎤 Вероника Тетеркина (вокал)", "adult": True, "child": False, "photo": "NikaTeterkina/NikaTeterkina.jpg", "desc": "Вероника Тетеркина"},
    {"name": "🎤 Полина Романовская (вокал)", "adult": True, "child": True, "photo": "PolinaRomanovskaya/SOLO01275.jpg", "desc": "Полина Романовская"},
    {"name": "🎤 Катя Калинкина (вокал)", "adult": True, "child": True, "photo": "KatyaKalinkina/KatyaKalinkina.jpg", "desc": "Катя Калинкина"},
    {"name": "🎤 Наташа Милованова (вокал)", "adult": False, "child": True, "photo": "NatashaMilovanova/NatashaMilovanova.jpg", "desc": "Наташа Милованова"}
]

def file_exists(filepath):
    return os.path.exists(filepath)

ADULT_TEACHERS = [t["name"] for t in ALL_TEACHERS if t["adult"]]
CHILD_TEACHERS = [t["name"] for t in ALL_TEACHERS if t["child"]]

TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Взрослые педагоги")],
        [KeyboardButton(text="👶 Детские педагоги")],
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True
)

ADULT_TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t)] for t in ADULT_TEACHERS] + [[KeyboardButton(text="⬅️ Назад к наставникам")]],
    resize_keyboard=True
)

CHILD_TEACHERS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t)] for t in CHILD_TEACHERS] + [[KeyboardButton(text="⬅️ Назад к наставникам")]],
    resize_keyboard=True
)

# ЗАЛЫ - ИСПРАВЛЕНО: 2 - СРЕДНИЙ, 3 - БОЛЬШОЙ
ROOMS_DATA = [
    ("miniroom", "🎤 Зал 1: Малый\n\n✅ Уютный зал с зеркалом\n✅ Электронное пианино\n✅ Вокальная стойка\n✅ Wi-Fi\n\nИдеально для записи вокала и сольных репетиций."),
    ("midleroom", "🎧 Зал 2: Средний\n\n✅ Телевизор для презентаций\n✅ Колонка-монитор\n✅ Микрофоны и стойка\n✅ Стулья\n✅ Wi-Fi\n\nОтлично подходит для групповых занятий, тренингов и индивидуальных занятий."),
    ("bigroom", "🎸 Зал 3: Большой\n\n✅ Сцена\n✅ Колонка-монитор\n✅ Беспроводной микрофон\n✅ Стойка\n✅ Дополнительные стулья\n✅ Wi-Fi\n\nДля подготовки к выступлениям и групповых занятий.")
]

# FAQ
FAQ_ANSWERS = {
    'faq_1': "💵 Стоимость занятий:\n\n• Индивидуальный пробный урок - 900 руб.\n• Пробный урок в группе - 850 руб.\n\n📞 По вопросам обращайтесь: +7-(913)-856-93-10",
    'faq_2': "⏰ Расписание:\n\n• Групповые занятия - после работы по будням\n• Индивидуальные уроки - по договоренности\n\n📞 Уточните расписание у администратора: +7-(913)-856-93-10",
    'faq_3': "📅 Регулярность занятий:\n\n• Для новичков: 3 раза в неделю\n• Для опытных: 2 раза в месяц\n• Минимальный курс: 3 месяца",
    'faq_4': "🎓 О педагогах:\n\n• Концертный опыт от 8 лет\n• Музыкальное образование\n• Лауреаты конкурсов\n• Любовь к музыке и саморазвитию",
    'faq_5': "📚 Структура урока:\n\n1️⃣ Определение целей\n2️⃣ Разминка и дыхание\n3️⃣ Вокальные упражнения\n4️⃣ Работа с репертуаром",
    'faq_6': "👶👵 Возраст:\n\n• От 3 до 50+ лет\n• В любом возрасте можно развить голос"
}

# Дипломы
TANIA_DIPLOMS = [
    ("🎓 IATS", "IATS", "Diplom Tania Swarz/diplom 1.1.png"),
    ("🎓 BIOPHONICS", "BIOPHONICS", "Diplom Tania Swarz/diplom 1.2.png"),
    ("🎓 Light Voice", "Light Voice", "Diplom Tania Swarz/diplom 1.3.png"),
    ("🎓 Профессиональное образование", "Профессиональное образование", "Diplom Tania Swarz/diplom 1.4.png"),
    ("🎓 Estil Voice", "Estil Voice", "Diplom Tania Swarz/diplom 1.5.png")
]

POLINA_DIPLOMS = [
    ("🎓 ESTIL VOICE", "🎓 ESTIL VOICE", "PolinaSharaeva/Diploms/1.png"),
    ("🎓 DIVA VOICE", "🎓 DIVA VOICE", "PolinaSharaeva/Diploms/2.png")
]

last_faq_messages = {}
ADMIN_ID = 1736644499


# Класс для анкеты
class LessonForm(StatesGroup):
    subject = State()
    name = State()
    contact = State()
    who = State()
    experience = State()
    goal = State()
    time = State()
    source = State()


async def send_welcome(message: types.Message):
    welcome_text = f"👋 Привет, {message.from_user.first_name}!\nЯ бот-помощник студии solo 🎙️\nВыберите интересующий вас раздел:"
    try:
        await message.answer_photo(photo=FSInputFile("solo.png"), caption=welcome_text)
    except:
        await message.answer(welcome_text)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await send_welcome(message)
    try:
        bonus_text = "🎁 Вступайте в наш телеграм канал, получите занятия в подарок или с хорошей скидкой ✌️🎶\n\nhttps://t.me/+EMU-EPeAfwlkYTFi"
        await message.answer_photo(photo=FSInputFile("bonus.png"), caption=bonus_text)
    except:
        bonus_text = "🎁 Вступайте в наш телеграм канал, получите занятия в подарок или с хорошей скидкой ✌️🎶\n\nhttps://t.me/+EMU-EPeAfwlkYTFi"
        await message.answer(bonus_text)
    await message.answer("🔽 Полезные ссылки:", reply_markup=USEFUL_LINKS_KEYBOARD)
    await send_main_menu(message)


# ==================== ОБРАБОТЧИКИ ПОЛЕЗНЫХ ССЫЛОК ====================

@dp.message(F.text == "❓ Частые вопросы")
async def faq_menu_reply(message: types.Message):
    builder = InlineKeyboardBuilder()
    faq_buttons = [
        ("💰 Стоимость", "faq_1"), ("⏰ Расписание", "faq_2"),
        ("📅 Регулярность", "faq_3"), ("🎓 Педагоги", "faq_4"),
        ("📚 Структура урока", "faq_5"), ("👶👵 Возраст", "faq_6")
    ]
    for i in range(0, len(faq_buttons), 2):
        builder.row(
            InlineKeyboardButton(text=faq_buttons[i][0], callback_data=faq_buttons[i][1]),
            InlineKeyboardButton(text=faq_buttons[i+1][0], callback_data=faq_buttons[i+1][1]), width=2
        )
    await message.answer("❓ Выберите вопрос:", reply_markup=builder.as_markup())


@dp.message(F.text == "⭐ Отзывы")
async def reviews_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Перейти в канал с отзывами", url="https://t.me/solo70_reviews")]])
    await message.answer("👥 Наш канал с отзывами:", reply_markup=keyboard)


@dp.message(F.text == "🏠 Наши залы")
async def rooms_reply(message: types.Message):
    for i, (room, text) in enumerate(ROOMS_DATA, 1):
        try:
            await message.answer_photo(photo=FSInputFile(f"rooms/{room}/room{i}.1.png"), caption=text)
        except:
            await message.answer(f"Фото зала {i} (1) не найдено")
        try:
            await message.answer_photo(photo=FSInputFile(f"rooms/{room}/room{i}.2.png"),
                                         caption=f"{'🎤' if i == 1 else '🎧' if i == 2 else '🎸'} Зал {i} - доп. ракурс")
        except:
            await message.answer(f"Фото зала {i} (2) не найдено")


@dp.message(F.text == "🌐 Сайт | Telegram")
async def site_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Наш сайт", url="https://solotomsk.ru"),
         InlineKeyboardButton(text="📱 Telegram канал", url="https://t.me/+EMU-EPeAfwlkYTFi")]
    ])
    await message.answer("🔗 Полезные ссылки:", reply_markup=keyboard)


@dp.message(F.text == "📍 Где мы находимся?")
async def ourplace_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 2ГИС", url="https://2gis.ru/tomsk/geo/422848120231246"),
         InlineKeyboardButton(text="🗺️ Яндекс Карты", url="https://yandex.ru/maps/67/tomsk/house/ulitsa_nikitina_8a/bE0YfwJpTUwPQFtsfXh2dnVmZA==/?ll=84.959497%2C56.477950&z=17")]
    ])
    await message.answer("📍 Мы на картах:", reply_markup=keyboard)


@dp.message(F.text == "🤫 Анонимный вопрос")
async def anonim_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤫 Задать анонимный вопрос", url="t.me/anonaskbot?start=kpsgjhclry2zs97u")]])
    await message.answer("📱 Нажмите кнопку ниже чтобы задать анонимный вопрос:", reply_markup=keyboard)


# ==================== ОБРАБОТЧИКИ ОСНОВНОГО МЕНЮ ====================

@dp.callback_query(lambda c: c.data == "info_lessons")
async def info_lessons_callback(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "📚 Структура урока по вокалу:\n\n"
        "1️⃣ Определение целей и способностей ученика\n"
        "2️⃣ Разминка и тренировка дыхания\n"
        "3️⃣ Упражнения для голоса\n"
        "4️⃣ Работа с репертуаром\n"
        "5️⃣ Подготовка к выступлению"
    )


@dp.callback_query(lambda c: c.data == "info_teachers")
async def info_teachers_callback(c: CallbackQuery):
    await c.answer()
    await c.message.answer("👥 Выберите категорию педагогов:", reply_markup=TEACHERS_KEYBOARD)


@dp.callback_query(lambda c: c.data == "info_price")
async def info_price_callback(c: CallbackQuery):
    await c.answer()
    await c.message.answer("💵 Расценки на обучение:\n\n⏳ Загружаю...")
    try:
        photo1 = FSInputFile("Price tags/raszenci1.jpg")
        await c.message.answer_photo(photo=photo1)
    except:
        pass
    try:
        photo2 = FSInputFile("Price tags/raszenci2.jpg")
        await c.message.answer_photo(photo=photo2)
    except:
        pass
    try:
        photo3 = FSInputFile("Price tags/raszenci3.jpg")
        await c.message.answer_photo(photo=photo3)
    except:
        pass


@dp.callback_query(lambda c: c.data == "start_trial")
async def start_trial_callback(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await state.set_state(LessonForm.subject)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎤 Вокал")], [KeyboardButton(text="🎸 Гитара")], [KeyboardButton(text="🪕 Укулеле")]], resize_keyboard=True, one_time_keyboard=True)
    await c.message.answer("🎯 Выберите предмет:", reply_markup=kb)


@dp.callback_query(lambda c: c.data == "start_enroll")
async def start_enroll_callback(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await state.set_state(LessonForm.subject)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎤 Вокал")], [KeyboardButton(text="🎸 Гитара")], [KeyboardButton(text="🪕 Укулеле")]], resize_keyboard=True, one_time_keyboard=True)
    await c.message.answer("🎯 Выберите предмет:", reply_markup=kb)


# ==================== АНКЕТА ====================

@dp.message(LessonForm.subject)
async def process_subject(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(LessonForm.name)
    await message.answer("📝 Введите ваше имя:")


@dp.message(LessonForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(LessonForm.contact)
    await message.answer("📞 Введите телефон или Telegram для связи:")


@dp.message(LessonForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(LessonForm.who)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="👶 Ребёнок (5-11)")], [KeyboardButton(text="🧑 Подросток(11-18)")], [KeyboardButton(text="👨 Взрослый(18+)")]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("👥 Кто будет заниматься?", reply_markup=kb)


@dp.message(LessonForm.who)
async def process_who(message: types.Message, state: FSMContext):
    await state.update_data(who=message.text)
    await state.set_state(LessonForm.experience)
    
    data = await state.get_data()
    subject = data.get('subject', '')
    
    if "Вокал" in subject:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Никогда")], [KeyboardButton(text="🎤 Немного для себя")], [KeyboardButton(text="📚 Занимался(ась)")], [KeyboardButton(text="🎭 Профессионально")]], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("🎵 Пробовали петь раньше?", reply_markup=kb)
    else:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Начинаю с нуля")], [KeyboardButton(text="🎸 Немного играл(а)")], [KeyboardButton(text="📚 Занимался(ась)")], [KeyboardButton(text="🎭 Профессионально")]], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("🎸 Играли на инструменте раньше?", reply_markup=kb)


@dp.message(LessonForm.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(LessonForm.goal)
    
    data = await state.get_data()
    who = data.get('who', '')
    
    base = [[KeyboardButton(text="🎤 Петь/играть для себя")], [KeyboardButton(text="🎭 Подготовиться к выступлению")], [KeyboardButton(text="💼 Развить навыки для работы")]]
    if "Ребёнок" in who:
        base.append([KeyboardButton(text="👶 Ребёнку для развития")])
    base.append([KeyboardButton(text="📝 Другое")])
    
    await message.answer("🎯 Что хотите получить от занятий?", reply_markup=ReplyKeyboardMarkup(keyboard=base, resize_keyboard=True, one_time_keyboard=True))


@dp.message(LessonForm.goal)
async def process_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(LessonForm.time)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🌅 Утро")], [KeyboardButton(text="☀️ День")], [KeyboardButton(text="🌙 Вечер")], [KeyboardButton(text="🤔 Любое, нужен совет")]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("⏰ Удобное время для занятий:", reply_markup=kb)


@dp.message(LessonForm.time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(LessonForm.source)
    await message.answer("🔍 Откуда вы о нас узнали? (напишите в свободной форме)")


@dp.message(LessonForm.source)
async def process_source(message: types.Message, state: FSMContext):
    await state.update_data(source=message.text)
    data = await state.get_data()
    
    admin_msg = (
        f"📝 НОВАЯ ЗАЯВКА!\n\n"
        f"🎯 Предмет: {data.get('subject')}\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Контакт: {data.get('contact')}\n"
        f"👥 Кто: {data.get('who')}\n"
        f"📊 Опыт: {data.get('experience')}\n"
        f"🎯 Цель: {data.get('goal')}\n"
        f"⏰ Время: {data.get('time')}\n"
        f"🔍 Откуда узнали: {data.get('source')}\n"
        f"🆔 ID пользователя: {message.from_user.id}\n"
        f"📱 Username: @{message.from_user.username if message.from_user.username else 'нет'}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        await message.answer("✅ Спасибо! Ваша заявка отправлена.\n\nМы свяжемся с вами в ближайшее время, чтобы подобрать удобное время и педагога. Без спама, только по делу 🧡")
    except Exception as e:
        await message.answer("❌ Ошибка отправки заявки.\n\nПожалуйста, свяжитесь с нами напрямую по телефону: +7-(913)-856-93-10")
        print(f"Ошибка отправки админу: {e}")
    
    await state.clear()


# ==================== ПЕДАГОГИ ====================

@dp.message(F.text == "👥 Взрослые педагоги")
async def adult_teachers(message: types.Message):
    await message.answer("👥 Взрослые педагоги:", reply_markup=ADULT_TEACHERS_KEYBOARD)


@dp.message(F.text == "👶 Детские педагоги")
async def child_teachers(message: types.Message):
    await message.answer("👶 Детские педагоги:", reply_markup=CHILD_TEACHERS_KEYBOARD)


async def send_teacher_info(message: types.Message, teacher: dict):
    descs = {
        "Таня Шварц": "👩‍🏫 Таня Шварц\n\n⭐ Опыт работы: 10 лет\n\n🎯 Помогу:\n• Поставить голос\n• Записать свою песню\n• Подготовиться к выступлению\n\n📚 Образование:\n• Колледж имени Эдисона, ТПУ\n• Курсы методики EVT (Италия)",
        "Полина Шараева": "👩‍🏫 Полина Шараева\n\n⭐ Опыт работы: 10 лет\n\n🎯 Джазовая певица, резидент @jazzcafeunderground\nРаботает с известными джазовыми музыкантами\n\n📚 Образование:\n• Курс Ольги Кляйн 2023\n• DIVA International 2024\n• Estill Voice training 2023",
        "Вероника Тетеркина": "👩‍🏫 Вероника Тетеркина\n\n🎯 Педагог по вокалу, вокалотерапевт\n• Работала в Германии\n• Особенный подход к каждому\n\n📚 ГСКТИИ, курс Ольги Кляйн\n\n⭐ Опыт: 8 лет",
        "Катя Беркетова": "👩‍🏫 Катя Беркетова\n\n🏆 Победитель конкурсов в Москве, СПб, Казани\n📺 Участник «Универвидение» на MTV\n✍️ Автор вокальных интенсивов\n\n📚 Образование:\n• ГКСКТИИ\n• СПбГИК (магистр)\n\n⭐ Опыт: 9 лет",
        "Полина Романовская": "👩‍🏫 Полина Романовская\n\n🎯 Детский педагог студии «Соло дети»\n• Дипломированный специалист\n• Лауреат конкурсов\n• Вокалистка группы «Tres Jolie»\n\n⭐ Опыт: более 3 лет",
        "Катя Калинкина": "👩‍🏫 Катя Калинкина\n\n🎯 Работает с дошкольниками и подростками\n• Руководитель коллектива «Мармеладки»\n• Победитель «Педагогический дебют» 2015\n\n📚 ТПУ, ТГПУ",
        "Наташа Милованова": "👩‍🏫 Наташа Милованова\n\n🎯 Руководитель детских вокальных групп\n• Педагог высшей категории\n• Лауреат конкурсов\n\n📚 Колледж имени Эдисона Денисова\n\n⭐ Опыт: 6 лет"
    }
    desc = descs.get(teacher["desc"], f"👩‍🏫 {teacher['desc']}")
    if file_exists(teacher["photo"]):
        try:
            await message.answer_photo(photo=FSInputFile(teacher["photo"]), caption=desc)
        except:
            await message.answer(desc)
    else:
        await message.answer(desc)


for teacher in ALL_TEACHERS:
    @dp.message(F.text == teacher["name"])
    async def teacher_handler(message: types.Message, t=teacher):
        await send_teacher_info(message, t)


# Дипломы
for text, cap, path in TANIA_DIPLOMS:
    @dp.message(F.text == text)
    async def diploma_tania(message: types.Message, p=path, c=cap):
        if file_exists(p):
            await message.answer_photo(photo=FSInputFile(p), caption=f"📜 {c}")
        else:
            await message.answer("❌ Фото диплома не найдено")

for text, cap, path in POLINA_DIPLOMS:
    @dp.message(F.text == text)
    async def diploma_polina(message: types.Message, p=path, c=cap):
        if file_exists(p):
            await message.answer_photo(photo=FSInputFile(p), caption=c)
        else:
            await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "🎓 Салют талантов")
async def d1(message: types.Message):
    if file_exists("NikaTeterkina/1.png"):
        await message.answer_photo(photo=FSInputFile("NikaTeterkina/1.png"), caption="🏆 Салют талантов")
    else:
        await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "🎓 Estill Voice")
async def d2(message: types.Message):
    if file_exists("NikaTeterkina/2.png"):
        await message.answer_photo(photo=FSInputFile("NikaTeterkina/2.png"), caption="🎓 Estill Voice")
    else:
        await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "🎓 Диплом ГКСКТИИ")
async def d3(message: types.Message):
    if file_exists("KatyaBerketova/diplom_gksktii.jpg"):
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_gksktii.jpg"), caption="🎓 ГКСКТИИ")
    else:
        await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "🎓 Диплом СПбГИК")
async def d4(message: types.Message):
    if file_exists("KatyaBerketova/diplom_spbgik.jpg"):
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_spbgik.jpg"), caption="🎓 СПбГИК, Магистр")
    else:
        await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "🏆 Дипломы конкурсов")
async def d5(message: types.Message):
    if file_exists("KatyaBerketova/diplom_konkursy.jpg"):
        await message.answer_photo(photo=FSInputFile("KatyaBerketova/diplom_konkursy.jpg"), caption="🏆 Дипломы конкурсов")
    else:
        await message.answer("❌ Фото диплома не найдено")

@dp.message(F.text == "📜 Дипломы")
async def diplomas_temp(message: types.Message):
    await message.answer("📜 Дипломы и сертификаты пока в разработке. Скоро добавлю! 🎓✨")


# Навигация
@dp.message(F.text == "⬅️ Назад к наставникам")
async def back_to_teachers_menu(message: types.Message):
    await message.answer("👥 Выберите категорию педагогов:", reply_markup=TEACHERS_KEYBOARD)


@dp.message(F.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    await send_welcome(message)
    await message.answer("🔽 Полезные ссылки:", reply_markup=USEFUL_LINKS_KEYBOARD)
    await send_main_menu(message)


@dp.callback_query(lambda c: c.data.startswith('faq_'))
async def faq_callback(c: CallbackQuery):
    await c.answer()
    if c.from_user.id in last_faq_messages:
        try:
            await bot.delete_message(chat_id=c.message.chat.id, message_id=last_faq_messages[c.from_user.id])
        except:
            pass
    sent = await c.message.answer(FAQ_ANSWERS.get(c.data, "❌ Ответ не найден"))
    last_faq_messages[c.from_user.id] = sent.message_id


async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
