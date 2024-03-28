/home/team/femmebabe/venv/bin/daphne -b 0.0.0.0 -e ssl:8008:privateKey=/etc/letsencrypt/live/femmebabe.com/privkey.pem:certKey=/etc/letsencrypt/live/femmebabe.com/cert.pem femmebabe.asgi:application
