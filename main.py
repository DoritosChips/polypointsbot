from telegram import *
from telegram.ext import *
from sheet_parser import Sheet
import os
from functools import partial
import json


TOKEN = os.environ.get('TOKEN')

ALL_NAMES = ['Айтынбетова Карина Рустамовна', 'Белозор Владислав Валентинович', 'Букреева Дарья', 'Вуколов Тимур Юрьевич', 'Горев Максим Андреевич', 'Зиссерман Елена Дмитриевна', 'Золотов Никита Михайлович', 'Ибрагимов Мухаммад ', 'Кишко Роман Дмитриевич', 'Коган Ольга Александровна', 'Колодяжный Александр Антонович', 'Крайнов Федор Павлович', 'Кузякин Леонид Дмитриевич', 'Левадный Егор Филиппович', 'Маркова Ольга Игоревна', 'Мостовой Николай Сергеевич', 'Петров Александр Олегович', 'Пицуха Григорий Викторович', 'Ральников Александр Максимович', 'Рожицын Владислав Алексеевич', 'Ромашов Иван Андреевич', 'Рустамов Хуршидбек Умидбек Угли', 'Сафонов Андрей Игоревич', 'Сидоров Даниил Михайлович', 'Слапик Алёна Игоревна', 'Смирнова Ирина Сергеевна', 'Соболь Владимир', 'Стрельникова Мария Александровна', 'Стригалев Андрей Андреевич', 'Хамдамжанова Феруза', 'Цой Кирилл Аркадьевич', 'Чабан Андрей Иванович', 'Шевелёва Вероника Анатольевна', 'Ярковая Людмила Алексеевна']

MAIN_MENU_BUTTONS = [["🔢Вышмат", "🍎Физика"], ["👤Изменить ФИО"]]

def mainMenu(update: Update, context: CallbackContext):
    if update.effective_chat.id not in NAMES:
        context.bot.send_message(chat_id=update.effective_chat.id, text="👤ФИО не задано", reply_markup=ReplyKeyboardMarkup([["👤Задать ФИО"]], resize_keyboard=True))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="🏠Главное меню", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))

    return ConversationHandler.END

def askForName(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="👤Введите ФИО", reply_markup=ReplyKeyboardRemove())

    return 0

def backupNames():
    with open("names.json", "w") as output:
        output.write(json.dumps(NAMES))

def setName(update: Update, context: CallbackContext):
    name = update.message.text
    if name not in ALL_NAMES:
        context.bot.send_message(chat_id=update.effective_chat.id, text="❌ФИО не найдено")
    else:
        NAMES[update.effective_chat.id] = name
        context.bot.send_message(chat_id=update.effective_chat.id, text="✅ФИО задано успешно")
    mainMenu(update, context)

    backupNames()

    return ConversationHandler.END

setNameConvHandler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("👤Задать ФИО"), askForName), MessageHandler(Filters.regex("👤Изменить ФИО"), askForName)],

    states={
        0: [MessageHandler(Filters.text, setName)]
    },

    fallbacks=[]
)

def viewMath(update: Update, context: CallbackContext):
    buttons = [["🏠На главную"], ["Итоговые баллы"], ["Баллы за сентябрь"], ["Баллы за октябрь"]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="🔢Вышмат", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

    return 0

def viewMathPoints(update: Update, context: CallbackContext, month: str = None):
    if month is None:
        values = math_sheet.getValues("Баллы итоговые!A2:B35")
        text = "Всего баллов: {}"
    else:
        match month:
            case "september":
                values = math_sheet.getValues("Баллы (сентябрь)!A2:B35")
                text = "Баллов за сентябрь: {}"
            case "october":
                values = math_sheet.getValues("Баллы (октябрь)!A2:B35")
                text = "Баллов за октябрь: {}"

    points = None
    for row in values:
        if row[0] == NAMES[update.effective_chat.id]:
            points = row[1]
            break
    if points is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="❌Баллы не найдены")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(points))
    
    mainMenu(update, context)

    return ConversationHandler.END

viewMathConvHandler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("🔢Вышмат"), viewMath)],

    states={
        0: [CommandHandler("start", mainMenu), MessageHandler(Filters.regex("🏠На главную"), mainMenu), MessageHandler(Filters.regex("Итоговые баллы"), viewMathPoints), MessageHandler(Filters.regex("Баллы за сентябрь"), partial(viewMathPoints, month="september")), MessageHandler(Filters.regex("Баллы за октябрь"), partial(viewMathPoints, month="october"))]
    },

    fallbacks=[]
)

def viewPhys(update: Update, context: CallbackContext):
    buttons = [["🏠На главную"], ["Пряники"]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="🍎Физика", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

    return 0

def viewPhysPoints(update: Update, context: CallbackContext):
    values = phys_sheet.getValues("Баллы!A2:B35")
    points = None
    for row in values:
        if row[0] == NAMES[update.effective_chat.id]:
            points = row[1]
            break
    if points is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="❌Баллы не найдены")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Всего пряников: {}".format(points))
    
    mainMenu(update, context)

    return ConversationHandler.END

viewPhysConvHandler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("🍎Физика"), viewPhys)],

    states={
        0: [CommandHandler("start", mainMenu), MessageHandler(Filters.regex("🏠На главную"), mainMenu), MessageHandler(Filters.regex("Пряники"), viewPhysPoints)]
    },

    fallbacks=[]
)

def updateSheets(update: Update = None, context: CallbackContext = None):
    global math_sheet
    math_sheet = Sheet('1hEngBbbJQkBpfTjC0qbcsZld-edUK8dinQwnQ8_PgSM')
    global phys_sheet
    phys_sheet = Sheet('1Tg4YYjRfXDSbrSAhNH3kEMp-ukiPejnuEECTy7NUS9Y')

def main():
    global NAMES
    if os.path.isfile("names.json"):
        NAMES = json.load(open("names.json"))
        NAMES = {int(i) : NAMES[i] for i in NAMES}
    else:
        NAMES = {}

    updateSheets()

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", mainMenu))
    dispatcher.add_handler(CommandHandler("update", updateSheets))
    dispatcher.add_handler(CommandHandler("menu", mainMenu))
    dispatcher.add_handler(setNameConvHandler)
    dispatcher.add_handler(viewMathConvHandler)
    dispatcher.add_handler(viewPhysConvHandler)

    updater.start_polling()

if __name__ == "__main__":
    main()