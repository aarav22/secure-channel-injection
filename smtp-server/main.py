import os
import ssl
import subprocess
from aiosmtpd.smtp import SMTP
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging
from aiosmtpd.smtp import AuthResult, LoginPassword

auth_db = {
    b"user1": b"password1",
    b"user2": b"password2",
    b"user3": b"password3",
}

# Name can actually be anything
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

# Create cert and key if they don't exist
if not os.path.exists('cert.pem') and not os.path.exists('key.pem'):
    subprocess.call('openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem ' +
                    '-days 365 -nodes -subj "/CN=localhost"', shell=True)

# Load SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('cert.pem', 'key.pem')



class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        peer = session.peer
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content         # type: bytes
        # Process message data...
        print('peer:' + str(peer))
        print('mail_from:' + str(mail_from))
        print('rcpt_tos:' + str(rcpt_tos))
        print('data:' + str(data))
        return '250 OK'
    
# Pass SSL context to aiosmtpd
# class ControllerStarttls(Controller):
#     def factory(self):
#         return SMTP(self.handler, 
#         auth_required=True,
#         require_starttls=True,
#         auth_callback=authenticator_func,
#         authenticator=authenticator_func,
#         tls_context=context)

# Start server
controller = Controller(CustomHandler(), authenticator=authenticator_func, auth_require_tls = False, auth_required=True, tls_context=context)
controller.start()
# print(controller.tls)
print(f'Server listening on port {controller.hostname}:{controller.port}')
input('Press any key to stop server...')
controller.stop()

