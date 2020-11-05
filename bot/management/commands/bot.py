import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater, CommandHandler, ConversationHandler
from telegram.utils.request import Request

from bot.management import commands
from bot.models import Profile


from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

# Bot Import

# Enable logging
logging.basicConfig(
    format=' ######### %(asctime)s - %(name)s - %(levelname)s - %(message)s #########',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Error log: {e} '
            print(error_message)
            raise e

    return inner


@log_errors
def start(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto start")
    text = """
    Listado de comando a usar:
    /info - Propósito del bot
    """
    update.message.reply_text(text)
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )


@log_errors
def info(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto info")
    update.message.reply_text("Este bot facilita la gestion de user MasterCard",
                              reply_markup=ReplyKeyboardRemove())


@log_errors
def prueba(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.effective_user.username}")
    id_group =0
    if update.effective_chat:
        id_group = update.effective_chat.id
    update.message.reply_text("Cantidad de usuarios en el chat "+str(id_group))


# Cancelar el registro
@log_errors
def cancel(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto cancelar")
    update.message.reply_text('Cancelada el registro')
    return ConversationHandler.END


# Iniciacion del comando `bot`
class Command(BaseCommand):
    help = "PrinterControlBot"

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )

        bot = Bot(
            request=request,
            token=settings.TOKEN,
        )
        update = Updater(
            bot=bot,
            use_context=True,
        )
        dp = update.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("info", info))
        dp.add_handler(CommandHandler("prueba", prueba))

        # Registar completp
#         conv_handler = ConversationHandler(
        # entry_points=[CommandHandler('registrar3d', registar3d)],

        # states={
        # REGISTEREMAIL: [MessageHandler(Filters.text, registeremail)],
        # TELEFONO: [MessageHandler(Filters.text, registrarphone),
        # CommandHandler('skip', skip_phone)],
        # PROVINCIA: [MessageHandler(Filters.text, registarProvincia)],
        # IS_PRINTER3D: [MessageHandler(Filters.regex('^(Si|No)$'), registar_isPrinter3D)],
        # CANT_FDM: [MessageHandler(Filters.text, register_FDM)],
        # DIAMETROFILAMENTO: [MessageHandler(Filters.text, registarDiametroFilamento)],
        # CANT_SLA_DLP: [MessageHandler(Filters.text, registarCant_SLA_DLP)],
        # IS_CNC: [MessageHandler(Filters.regex('^(Si|No)$'), register_isCNC)],
        # CNC: [MessageHandler(Filters.text, register_CNC)],
        # MATERIAL_CNC: [MessageHandler(Filters.text, registerMaterialCNC)],
        # RESERVA: [MessageHandler(Filters.text, registarMateriles)],
        # CANTPETG: [MessageHandler(Filters.text, registarCantPETG)],
        # },

        # fallbacks=[CommandHandler('cancel', cancel)],

        # )
        # dp.add_handler(conv_handler)

        # # Regsitrar solo CNC
        # registar_CNC_Only = ConversationHandler(
        # entry_points=[CommandHandler('registrar_cnc', registarCNCOnly)],

        # states={
        # CNC: [MessageHandler(Filters.text, register_CNC)],
        # MATERIAL_CNC: [MessageHandler(Filters.text, registerMaterialCNC)],
        # },

        # fallbacks=[CommandHandler('cancel', cancel)],

        # )
        # dp.add_handler(registar_CNC_Only)
        update.start_polling()
        print('I live')
        update.idle()
