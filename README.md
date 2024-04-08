## Public server
# 172.104.229.159

## Install instructions
# Client
- clone repository (standalone releases coming soon)
- inside the main folder, install dependencies (using pip install -r requirements.txt, poetry shell > poetry install, or any other venv you might be using)
- inside src/client, run main.py
- client will autogenerate settings file, change the default value of the HOST to the ip of the server you are using (172.104.229.159 for the public one)
- enjoy the suffering of this UX nightmare

# Server
- clone repository
- inside the main folder, do docker-compose up
- distribute the server's ip to whoever you want to use your server

## Troubleshooting
# Client won't start
- Make sure you are starting main.py within the right context (from within termsync/src/client)
- Make sure you didn't delete the data folder or any other files

# Client won't connect to the server
- Make sure you changed the default HOST within data/settings.yaml
- Make sure you are using the correct port (2727 by default, can be changed from Dockerfile and docker-compose.yaml)
