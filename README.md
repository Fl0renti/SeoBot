# SeoBot
 
To start using SEO Bot first download this as zip or as git repo

1. After unzipping, go to Server Folder.
2. Open command prompt in that folder and type pip install pipenv
3. in Command prompt write pipenv shell, to create a virtual environment or create it in another way
4. After creating the virtual environment, install requirements.txt by typing pipenv install -r requirements.txt
5. Type in command prompt python manage.py makemigrations
6. Type python manage.py migrate
7. python manage.py createsuperuser, to create a super user.
8. python manage.py runserver


After setting up the Server, go back to Bot
1. cd ../Bot
2. pipenv shell (to create a virtual environment)
3. pipenv install -r requirements.txt
4. if that didnt work out, type pipenv install selenium webdriver-manager pyautogui
5. if that didnt work out either, pip install selenium webdriver-manager pyautogui
6. python StartApp.py

After setting upp both of them, u can go ahead and use ur interface in: 127.0.0.1:8000 or in ur server where you are running the project
