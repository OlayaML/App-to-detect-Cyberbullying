'''
@author: olayamoranlevas
'''

import asyncio
import sys
from getpass import getpass

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.network import ConnectionTcpAbridged
from telethon.utils import get_display_name

# Creamos una variable global para manejar el bucle que estaremos usando
loop = asyncio.get_event_loop()


def sprint(string, *args, **kwargs):
    """Safe Print (se encarga de UnicodeEncodeErrors en algunos terminales)"""
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore')\
                       .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)


def print_title(title):
    """Funcion de ayuda para imprimir titulos"""
    sprint('\n')
    sprint('=={}=='.format('=' * len(title)))
    sprint('  {}  '.format(title))
    sprint('=={}=='.format('=' * len(title)))


def bytes_to_string(byte_count):
    """Convierte un recuento de bytes en string (en KB, MB...)"""
    suffix_index = 0
    while byte_count >= 1024:
        byte_count /= 1024
        suffix_index += 1

    return '{:.2f}{}'.format(
        byte_count, [' bytes', 'KB', 'MB', 'GB', 'TB'][suffix_index]
    )


async def async_input(prompt):
    """
    La input() de Python esta bloqueda, lo que significa que el bluce de evento que creamos
    no puede ejecutarse mientras estemos bloqueando. Este método permitirá que el bucle se 
    ejecute mientras esperamos la entrada.
    """
    print(prompt, end='', flush=True)
    return (await loop.run_in_executor(None, sys.stdin.readline)).rstrip()


class InteractiveTelegramClient(TelegramClient):

    def __init__(self, session_user_id, api_id, api_hash,
                 proxy=None):
        """
        Inicializa el Cliente de Telegram
        :param session_user_id: Nombre del archivo de *.session.
        :param api_id: Telegram's api_id.
        :param api_hash: Telegram's api_hash.
        :param proxy: Proxy opcional tuple/dictionary.
        """
        print_title('INITIALIZATION')

        print('Initializing the Telegram Client...')

        # El primer paso es inicializar el cliente de telegram, como lo estamos 
        # subclasificando necesitamos llamar a super () .__ init __ ()
        
        super().__init__(session_user_id, api_id, api_hash,

            # Opcionalmente podemos cambiar el tipo de conexion.
            # Esto cambia la apariencia de los paquetes enviados.
            # Por defecto: ConnectionTcpFull, el + pequeño es: ConnectionTcpAbridged.
            connection=ConnectionTcpAbridged,

            # Si utilizamos proxy lo introducimos aqui.
            proxy=proxy)

        # Almacenamos el mapa aqui {message.id: message} para poder descargar la media
        # de los mensajes que la tengan.
        self.found_media = {}

        # Llamar a .connect() puede provocar un error de conexion falso, por lo que debemos
        # crear una excepcion antes de continuar.
        print('Connecting to Telegram servers...')
        try:
            loop.run_until_complete(self.connect())
        except ConnectionError:
            print('Initial connection failed. Retrying...')
            loop.run_until_complete(self.connect())

        # Si el usuario aún no ha llamado a .sign_in () o .sign_up (), no estara autorizado. 
        # Lo primero que debemos hacer es autorizar. La llamada a .sign_in () solo debe hacerse 
        # una vez, ya que la información se guarda en el archivo * .session para que no tenga 
        # que ingresar el codigo todas las veces.
        if not loop.run_until_complete(self.is_user_authorized()):
            print('First run. Sending code request...')
            print('REMEMBER: Phone Format is +34629****17')
            user_phone = input('Enter your phone: ')
            loop.run_until_complete(self.sign_in(user_phone))

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user =\
                        loop.run_until_complete(self.sign_in(code=code))

                # La verificación en dos pasos puede estar habilitada, y .sign_in 
                # generará este error. En ese caso, solicite la contraseña.
                except SessionPasswordNeededError:
                    pw = getpass('Two step verification is enabled. '
                                 'Please enter your password: ')

                    self_user =\
                        loop.run_until_complete(self.sign_in(password=pw))

    async def run(self):
        """Bucle principal del Cliente de Telegram, esperara a la accion del usuario"""

        # Una vez que todo este listo, podemos añadir un controlador de eventos.
        # Los eventos son "las actualizaciones de telegram"
        self.add_event_handler(self.message_handler, events.NewMessage)

        # Introducimos un bucle while para chatear tanto como el usuario quiera.
        while True:
            # Recuperamos los dialogos. Podemos establecer el limite en ninguno o
            # recuperarlos todos si asi lo quisieramos, pero esto llevaria tiempo.
            dialog_count = 15

            # Las entidades representan al usuario, al chat o al canal.
            dialogs = await self.get_dialogs(limit=dialog_count)

            i = None
            while i is None:
                print_title('DIALOGS WINDOW')

                # Los mostramos para que el usuario pueda elegir
                for i, dialog in enumerate(dialogs, start=1):
                    sprint('{}. {}'.format(i, get_display_name(dialog.entity)))

                # Dejamos que el usuario decida con quien quiere hablar
                print()
                print('> Choose the dialog number to retrieve the messages')
                print()
                print('> Other options:')
                print('  !q: Quits the dialogs window and exits.')
                print('  !l: Logs out, terminating this session.')
                print()
                i = await async_input('Enter dialog ID or a command: ')
                if i == '!q':
                    return
                if i == '!l':
                    # El cierre de sesión hará que el usuario tenga que volver a ingresar 
                    # el código la próxima vez que quiera usar la biblioteca, también eliminará 
                    # el archivo * .session del sistema de archivos. Esto no es lo mismo que llamar 
                    # a .disconnect (), que simplemente apaga todo.
                    await self.log_out()
                    return

                try:
                    i = int(i if i else 0) - 1
                    # Comprobamos que el comando es valido (numero del usuario, chat o canal)
                    if not 0 <= i < dialog_count:
                        i = None
                except ValueError:
                    i = None

            # Recuperamos el usuario seleccionado (o chat, o canal)
            entity = dialogs[i].entity
            print_title('Dialog with "{}"'.format(get_display_name(entity)))              
            
            # HISTORIAL
            # Primero recuperamos los mensajes
            messages = await self.get_messages(entity, limit=10)
                # Iteramos en orden inverso para que aparezcan ordenados
                # en la consola y los imprimimos con el formato:
                # "[hh:mm] Sender: Message"
            for msg in reversed(messages):
                    # Como hicimos una llamada a la API usando el cliente propio, 
                    # siempre tendrá información sobre el remitente, (msg.sender).
                    name = get_display_name(msg.sender)

                    # Formato del contenido del mensaje.
                    if getattr(msg, 'media', None):
                        self.found_media[msg.id] = msg
                        content = '<{}> {}'.format(
                            type(msg.media).__name__, msg.message)

                    elif hasattr(msg, 'message'):
                        content = msg.message
                    elif hasattr(msg, 'action'):
                        content = str(msg.action)
                    else:
                        # Mensaje desconocido, simplemente imprimimos su nombre de clase
                        content = type(msg).__name__

                    # Y lo imprimimos al usuario.
                    sprint('[{}:{}] (ID={}) {}: {}'.format(
                        msg.date.hour, msg.date.minute, msg.id, name, content))
            while True:      
            # Y comienza el bucle while para chatear
                print()
                print('!q:  Quits the current chat.')
                print('!Q:  Quits the current chat and exits.')
                print()
                msg = await async_input('Enter a message: ')
                # CERRAR
                if msg == '!q':
                    break
                elif msg == '!Q':
                    return
                # Mandar un mensaje (si lo hay)
                elif msg:
                    await self.send_message(entity, msg, link_preview=False)
        
    @staticmethod
    def print_progress(progress_type, downloaded_bytes, total_bytes):
        print('{} {} out of {} ({:.2%})'.format(
            progress_type, bytes_to_string(downloaded_bytes),
            bytes_to_string(total_bytes), downloaded_bytes / total_bytes))

    @staticmethod
    def download_progress_callback(downloaded_bytes, total_bytes):
        InteractiveTelegramClient.print_progress(
            'Downloaded', downloaded_bytes, total_bytes)

    @staticmethod
    def upload_progress_callback(uploaded_bytes, total_bytes):
        InteractiveTelegramClient.print_progress(
            'Uploaded', uploaded_bytes, total_bytes)

    async def message_handler(self, event):
        """Devolucion de llamada para los events.NewMessage recibidos"""

        # Llamamos a message_handler cuando se producen actualizaciones de Telegram.
        chat = await event.get_chat()
        if event.is_group:
            if event.out:
                sprint('>> sent "{}" to chat {}'.format(
                    event.text, get_display_name(chat)
                ))
            else:
                sprint('<< {} @ {} sent "{}"'.format(
                    get_display_name(await event.get_sender()),
                    get_display_name(chat),
                    event.text
                ))
        else:
            if event.out:
                sprint('>> "{}" to user {}'.format(
                    event.text, get_display_name(chat)
                ))
            else:
                sprint('<< {} sent "{}"'.format(
                    get_display_name(chat), event.text
                ))


if __name__ == '__main__':
    SESSION = 'telegram_client_msg'
    API_ID = 467656
    API_HASH = '7125eb305f70aee52d077e5c564aaed1'
    client = InteractiveTelegramClient(SESSION, API_ID, API_HASH)
    loop.run_until_complete(client.run())