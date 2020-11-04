import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater, CommandHandler, ConversationHandler
from telegram.utils.request import Request

from bot.management import commands
from bot.models import Profile

# Bot Import

# Enable logging
logging.basicConfig(
    format=' ######### %(asctime)s - %(name)s - %(levelname)s - %(message)s #########',
    level=logging.INFO)

logger = logging.getLogger(__name__)

provincias = [
    ['Pinar del Río',
     'Artemisa'],
    ['Mayabeque',
     'Matanzas'],
    ['Cienfuegos',
     'Villa Clara'],
    ['Sancti Spiritus',
     'Ciego de Ávila'],
    ['Camagüey',
     'Las Tunas'],
    ['Holguín',
     'Granma'],
    ['Santiago de Cuba',
     'Guantánamo'],
    ['Isla de la Juventud',
     'Habana'],
]
# Para registar el usuario
REGISTEREMAIL, PROVINCIA, TELEFONO, IS_PRINTER3D, YES_IS_PRINTER3D, NO_IS_PRINTER3D, CANT_FDM, DIAMETROFILAMENTO, \
    CANT_SLA_DLP, IS_CNC, CNC, RESERVA, MATERIAL_CNC, CANTPETG, ONLYCNC = range(15)


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
    /registrar3d - Homologo de las preguntas de lista de  https://bit.ly/cuba-3dprinters
    /cancel - Cancela el proceso de registro
    /registrar_cnc - Registrar el CNC
    /recibir_pla - Notificar recepción de filamento PLA
    /recibir_petg - Notificar recepción de filamento PETG
    /recibir_abs - Notificar recepción de filamento ABS
    /recibir_pvc - Notificar recepción de filamento PVC
    /recibir_pantallas  - Notificar recepción de placas transparentes para viseras
    /recibir_acrilico - Notificar recepción de planchas de acrílico
    /reportar_viseras - Notificar cantidad de viseras hechas
    /entregar_viseras - Notificar cantidad de viseras entregadas
    /resumen - Resúmen de las viseras y material entregado
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
    update.message.reply_text("Este bot facilita la gestion de impresionn 3D",
                              reply_markup=ReplyKeyboardRemove())


# Empezar el registar
@log_errors
def registar3d(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registar3d")
    update.message.reply_text("Por favor introduzca el correo",
                              reply_markup=ReplyKeyboardRemove())
    return REGISTEREMAIL


# Registar los email
@log_errors
def registeremail(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registeremail")
    email = str(update.message.text)
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )
    p.email = email
    p.save()
    update.message.reply_text(
        "Por favor inserte su # de telefono , si no lo deseas /skip para pasar", reply_markup=ReplyKeyboardRemove())
    return TELEFONO


# Omitir el telefono
@log_errors
def skip_phone(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto skip_phone")
    update.message.reply_text(
        "Cual es su provincia?",
        resize_keyboard=True,
        reply_markup=ReplyKeyboardMarkup(provincias),
        one_time_keyboard=True)
    return PROVINCIA


# Registar el telefono
@log_errors
def registrarphone(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registerphone")
    telefono = str(update.message.text)
    if telefono == "/skip":
        update.message.reply_text("Bueno despues puede poner el # si desea")
    else:
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.telefono = telefono
        p.save()

    update.message.reply_text(
        "Cuál es su provincia?",
        resize_keyboard=True,
        reply_markup=ReplyKeyboardMarkup(provincias),
        one_time_keyboard=True)
    return PROVINCIA


# Registar la provincia
@log_errors
def registarProvincia(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registarProvincia")
    provincia = str(update.message.text)
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )
    p.provincia = provincia
    p.save()
    update.message.reply_text(
        f"Provincia actualizada {provincia}", reply_markup=ReplyKeyboardRemove())
    reply_keyboard = [['Si', 'No', ]]
    update.message.reply_text(
        "Tienes impresora?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
        one_time_keyboard=True)
    return IS_PRINTER3D


# Register si Printer3d
@log_errors
def registar_isPrinter3D(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto isPrinted3D")
    is_printer = (update.message.text == "Si")
    if is_printer:
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.is_3d = True
        p.save()
        update.message.reply_text(
            "El objetivo es determinar la capacidad fuerza de trabajo en maquinaria total disponible"
            " que puede ser destinada a estos fines. \n\n"
            "¿De cuántas impresoras FDM dispone? ", reply_markup=ReplyKeyboardRemove())
        return CANT_FDM
    else:
        reply_keyboard = [['Si', 'No', ]]
        update.message.reply_text("Tienes herramientas CNC?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                                  one_time_keyboard=True
                                  )
        return IS_CNC


# FDM disponible
@log_errors
def register_FDM(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto register_FDM")
    try:
        cant_fdm = int(update.message.text)
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.cant_fdm = cant_fdm
        p.save()
        update.message.reply_text(
            "¿Qué diámetros de filamento plástico puede utilizar su impresora? \n"
            " Ejemplo : 1.75 mm, 2.85mm")
        return DIAMETROFILAMENTO
    except ValueError:
        update.message.reply_text("Debe de introducir un número")


# Registar Diametro Filamento
@log_errors
def registarDiametroFilamento(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto Diametro Filamento")
    dia_fila = str(update.message.text)
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )
    p.diametro_filamento = dia_fila
    p.save()
    update.message.reply_text("¿De cuántas impresoras SLA o DLP dispone?")
    return CANT_SLA_DLP


# Registar cantidad SLA o DLP
@log_errors
def registarCant_SLA_DLP(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registerCant_SLA_DLP")
    try:
        cant_SLA_DLP = int(update.message.text)
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.cant_printerSLA_DLP = cant_SLA_DLP
        reply_keyboard = [['Si', 'No', ]]
        update.message.reply_text("Tienes herramientas CNC?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                                  one_time_keyboard=True
                                  )
        return IS_CNC
    except ValueError:
        update.message.reply_text("Debe de introducir un numero")


# Registar si ahi CNC
@log_errors
def register_isCNC(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto register_isCNC")
    is_cnc = (update.message.text == "Si")
    if is_cnc is True:
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.is_cnc = True
        update.message.reply_text(
            "El objetivo es determinar la capacidad fuerza de trabajo en maquinaria total disponible que puede ser "
            "destinada a estos fines./n "
            "¿De cuántas máquinas CNC dispone?", reply_markup=ReplyKeyboardRemove())
        return CNC
    else:
        update.message.reply_text(
            "Reservas de material para tomar decisiones y priorizar objetivos de impresión."
            "\n Si deseas insertar los datos despues solo escriba /cancel\n"
            "¿De cuántos kg de filamento PLA para impresión dispone?", reply_markup=ReplyKeyboardRemove()
        )
        return RESERVA


# Registar cantidad de CNC
@log_errors
def register_CNC(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto register_CNC")
    try:
        cant = int(update.message.text)
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.cant_cnc = cant
        p.save()

        update.message.reply_text(
            "¿Con qué materiales puede trabajar su máquina herramienta CNC? "
            "Ejemplo: Acrílico, Madera, PVC ")
        return MATERIAL_CNC
    except ValueError:
        update.message.reply_text("Debe de introducir un numero")


# Registrar MaterialCNC
@log_errors
def registerMaterialCNC(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registerMaterialCNC")
    material = str(update.message.text)
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )
    p.materiales_cnc = material
    p.save()
    print(commands.IS_ONLY_CNC)
    if not commands.IS_ONLY_CNC:
        update.message.reply_text(
            "Reservas de material para tomar decisiones y priorizar objetivos de impresión."
            "\n Si deseas insertar los datos despues solo escriba /cancel\n"
            "¿De cuántos kg de filamento PLA para impresión dispone?", reply_markup=ReplyKeyboardRemove()
        )
        return RESERVA
    else:
        update.message.reply_text("Gracias por actualizar su CNC")
        return ConversationHandler.END


# Registar Materiales
@log_errors
def registarMateriles(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registarMateriales")
    try:
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        cant = int(update.message.text)
        p.cant_pla = cant
        p.save()
        update.message.reply_text("¿De cuántos kg de filamento PETG para impresión dispone?",
                                  reply_markup=ReplyKeyboardRemove())
        return CANTPETG
    except ValueError:
        update.message.reply_text("Inserte un número")


def registarCantPETG(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registarCantPETG")

    try:
        petg = int(update.message.text)
        p, _ = Profile.objects.get_or_create(
            external_id=update.message.from_user.id,
            defaults={
                'username': update.message.from_user.username,

            }
        )
        p.cant_petg = petg
        p.save()
        update.message.reply_text("¿De cuántos kg de filamento ABS para impresión dispone?")
    except ValueError:
        update.message.reply_text("Inserte un numero")


# Cancelar el registro
@log_errors
def cancel(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto cancelar")
    update.message.reply_text('Cancelada el registro')
    return ConversationHandler.END


def registarCNCOnly(update: Update, context: CallbackContext):
    logger.info(f"El usuario {update.message.from_user.username} consulto registarCNCOnly")
    p, _ = Profile.objects.get_or_create(
        external_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.username,

        }
    )
    p.is_cnc = True
    p.save()
    commands.IS_ONLY_CNC = True
    update.message.reply_text(
        "El objetivo es determinar la capacidad fuerza de trabajo en maquinaria total disponible que puede ser "
        "destinada a estos fines./n "
        "¿De cuántas máquinas CNC dispone?", reply_markup=ReplyKeyboardRemove())
    return CNC


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

        # Registar completp
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('registrar3d', registar3d)],

            states={
                REGISTEREMAIL: [MessageHandler(Filters.text, registeremail)],
                TELEFONO: [MessageHandler(Filters.text, registrarphone),
                           CommandHandler('skip', skip_phone)],
                PROVINCIA: [MessageHandler(Filters.text, registarProvincia)],
                IS_PRINTER3D: [MessageHandler(Filters.regex('^(Si|No)$'), registar_isPrinter3D)],
                CANT_FDM: [MessageHandler(Filters.text, register_FDM)],
                DIAMETROFILAMENTO: [MessageHandler(Filters.text, registarDiametroFilamento)],
                CANT_SLA_DLP: [MessageHandler(Filters.text, registarCant_SLA_DLP)],
                IS_CNC: [MessageHandler(Filters.regex('^(Si|No)$'), register_isCNC)],
                CNC: [MessageHandler(Filters.text, register_CNC)],
                MATERIAL_CNC: [MessageHandler(Filters.text, registerMaterialCNC)],
                RESERVA: [MessageHandler(Filters.text, registarMateriles)],
                CANTPETG: [MessageHandler(Filters.text, registarCantPETG)],
            },

            fallbacks=[CommandHandler('cancel', cancel)],

        )
        dp.add_handler(conv_handler)

        # Regsitrar solo CNC
        registar_CNC_Only = ConversationHandler(
            entry_points=[CommandHandler('registrar_cnc', registarCNCOnly)],

            states={
                CNC: [MessageHandler(Filters.text, register_CNC)],
                MATERIAL_CNC: [MessageHandler(Filters.text, registerMaterialCNC)],
            },

            fallbacks=[CommandHandler('cancel', cancel)],

        )
        dp.add_handler(registar_CNC_Only)
        update.start_polling()
        print('I live')
        update.idle()
