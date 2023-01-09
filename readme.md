Used openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost' to generate a self signed cert.
then python -m aiosmtpd -n --tlscert .\cert.pem --tlskey .\key.pem --d --d --d  to start the SMTP server

Developed in Python 3.8.0