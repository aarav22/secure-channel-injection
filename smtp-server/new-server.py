from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as Server, syntax
import asyncio
import ssl
import subprocess
import os
from database import (Database, User)
from aiosmtpd.smtp import AuthResult, LoginPassword

auth_db = {
    b"user1": b"password1",
    b"user2": b"password2",
    b"user3": b"password3",
}



def authenticator_func(server, session, envelope, mechanism, auth_data):
    # For this simple example, we'll ignore other parameters
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password
    # If we're using a set containing tuples of (username, password),
    # we can simply use `auth_data in auth_set`.
    # Or you can get fancy and use a full-fledged database to perform
    # a query :-)
    if auth_db.get(username) == password:
        return AuthResult(success=True)
    else:
        return AuthResult(success=False, handled=False)


class SMTPServer(Server):
    @syntax('PING [ignored]')
    async def smtp_PING(self, arg):
        await self.push('259 Pong')

    @syntax("AUTH USERNAME PASSWORD [ignored]")
    async def smtp_AUTH(self, arg):
        if arg is None:
            await self.push('501 Syntax: AUTH USERNAME PASSWORD [ignored]')
            return
        else:
            credentials = arg.split(' ')
            if len(credentials) != 2:
                await self.push('501 Syntax: AUTH USERNAME PASSWORD [ignored]')
                return
            else:
                database = Database('network_project.db')
                if database.check_credentials(credentials[0], credentials[1]):
                    await self.push('253 Authentication successful')                    
                else:
                    await self.push('535 Invalid credentials')

    @syntax("REG USERNAME PASSWORD [ignored]")
    async def smtp_REG(self, arg):
        if arg is None:
            await self.push('501 Syntax: REG USERNAME PASSWORD [ignored]')
            return
        else:
            credentials = arg.split(' ')
            if len(credentials) != 2:
                await self.push('501 Syntax: REG USERNAME PASSWORD [ignored]')
                return
            else:
                database = Database('network_project.db')
                database.add_account(credentials[0], credentials[1])
                await self.push('253 Authentication successful')

    # uses custom response code: '255 user_id'
    @syntax("GETUSER USERNAME PASSWORD")
    async def smtp_GETUSER(self, arg):
        if arg is None:
            await self.push('501 Syntax: GETUSER USERNAME PASSWORD [ignored]')
            return
        else:
            credentials = arg.split(' ')
            if len(credentials) != 2:
                await self.push('501 Syntax: GETUSER USERNAME PASSWORD [ignored]')
                return
            else:
                database = Database('network_project.db')
                user_id = database.get_user_id(credentials[0], credentials[1])
                response = '255 ' + str(user_id)
                await self.push(response)


class SMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:')
        print(envelope.content.decode('utf8', errors='replace'))
        print('End of message\n')

        database = Database('network_project.db')
        user_id = database.get_user_id_server(envelope.rcpt_tos[0])
        if(user_id != -1):
            database.save_email(user_id, envelope)
            return '250 Message accepted for delivery'
        else:
            return '550 No such recepient exist'

        
class MyController(Controller):
    def factory(self):
        if not os.path.exists('cert.pem') and not os.path.exists('key.pem'):
            subprocess.call("openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'",shell=True)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('cert.pem', 'key.pem')
        return SMTPServer(self.handler, tls_context=context, authenticator=authenticator_func, require_starttls=True)


if __name__ == '__main__':
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        controller = MyController(SMTPHandler())    
        print(controller.hostname)
        print(controller.port)
        controller.start()
        input("Server started. Press Return to quit.\n")
    except KeyboardInterrupt:
        print('stopped')
        controller.stop()