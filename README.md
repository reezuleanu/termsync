<p align = "center">
<img width="692" alt="Screenshot 2024-04-09 at 20 30 46" style = "justify-content:center;" src="https://github.com/reezuleanu/termsync/assets/37458482/f81bf194-c051-4d20-9f20-f35d1d5fd1c3">
</p>

# What is TermSync
Termsync is a novelty, open-source python CLI project management tool. It allows you to create projects and tasks, asign people to them, update the progress for the whole team to see, and so on, all from your terminal. 

# Public server
#### http://172.104.229.159:2727/

# Getting started
### Logging in
To get started using TermSync, you first need to install the client and have a server to use (check 'Install instructions'). After that's all done, you can get started using TermSync.

![](https://github.com/reezuleanu/termsync/blob/main/documentation/getting_started1.gif)
To use the app, you will need an account. Either use 'register' to create an account, or use 'login' to login with an existing one.

### Commands
Once you are logged in, the world is yours. Use 'help' to see what commands are available and how to use them.

![](https://github.com/reezuleanu/termsync/blob/main/documentation/getting_started2.gif)

### What exactly can you do?
In TermSync, you can search for users, see their public details, add them to your projects. Or if you are an admin, edit and delete their accounts (it's just a prank). See 'help user' for more.
##### COMING SOON: messaging, profile pictures

![](https://github.com/reezuleanu/termsync/blob/main/documentation/getting_started3.gif)

The main feature is the projects. You can create projects and add tasks to track your team's progress. See 'help project' for more.
##### COMING SOON: progress bars, changes highlighting

![](https://github.com/reezuleanu/termsync/blob/main/documentation/getting_started4.gif)

# Install instructions
### Client
1. clone repository to run from source. Alternatively, on Windows, you can download the latest standalone release and run the executable. In that case, skip to step 4.
2. inside the main folder, install dependencies (using pip install -r requirements.txt, poetry shell > poetry install, or any other venv you might be using)
3. inside src/client, run main.py
4. client will auto-generate settings file, change the default value of the HOST to the ip of the server you are using (172.104.229.159 for the public one)
5. enjoy the suffering of this UX nightmare

### Server
- clone repository
- inside the main folder, do 'docker-compose up'
- distribute the server's ip to whoever you want to use your server

# Troubleshooting
### Client won't start
- Make sure you are starting main.py within the right context (from within termsync/src/client)
- Make sure you didn't delete the data folder or any other files

### Client won't connect to the server
- Make sure you changed the default HOST within data/settings.yaml
- Make sure you are using the correct port (2727 by default, can be changed from Dockerfile and docker-compose.yaml)

# Tests
Currently, there are only mock tests for the API (not full coverage), and none for the client.

# Pull requests
As this project is for me to improve my programming skills and impress potential recruiters, this repo does not accept pull requests.
