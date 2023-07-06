## Project name
qapp - quality assurance app based on Django.

## Table of contents
- [Project name](#project-name)
- [Table of contents](#table-of-contents)
- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
- [Usage](#usage)

## General info
During work for one of biggest Polish company related to design & production of city cars,
I participated in quality control of these vehicles on all levels. At the beginning, inspections
were made using classic paper sheets. After some time, managers decided that it would be good to use some software/application
to handle this process. In results of this, an Java app (IBM Lotus Notes/Domino environment) was created. 
Unfortunately, due to lack of developers only two version were released.
Disadvantages of app:
* app was build in very 'exclusive' environment (even if it is Java, there are not enough IBM-Domino developers on market)
* code is very complicated - there are a lot of 'if' statements,
* app is not native; it works only inside Lotus Notes Client,
* problem with access to application via VPN,
* no support for mobile devices,
* the app is insanely slow.

I have decided to show some proof-of-concept, that developing and maintaining those type of apps can be easy.
Advantages of qapp:
- app is a Python app (very popular language),
- core for app is Django, which is open-source and very popular Python web framework,
- code is simplified, a lot of Django-native mechanisms and solutions are used,
- for running as web service, there is no VPN necessary - app can be published on public http server,
- support for mobile devices & computers.

Extra features in qapp that are not supported in original app:
  
* easy way to ad new categories (custom ListView),  
* editing of existing Gate(s) object(s) without special permissions 
(permissions can be granted via admin panel),  
* multi-adding (possibility to add one Gate to more than one parent object),  
* multi-accepting (possibility to change status for multiple Gate(s) in one click),  
* possibility to upload photo/file directly from mobile phone during inspection,  
* resizing photos on client-side (reduce file size on client side and server side; speeding up process),  
* logs for each Gate object (each action or change is logged in log page),  
* friendly and fast filtering of objects,
* current status for logged user: how many Gate objects was declined by QA etc.  
  
## Technologies
* Backend: Python3 + Django,
* Frontend: HTML + CSS + JavaScript
* Database: SQLite (for prod environment PostgreSQL is recommended)

Code was tested on following platforms:
* Ubuntu 16.04.1 LTS (GNU/Linux 2.6.32-openvz-042stab125.5-amd64 x86_64) with Python 3.5.2 (server-side),
* Windows 7 x64 (Opera 58 + Firefox 65) (client-side),
* Android 8.0 (Galaxy S7) (client-side),
* Android 8.1.1 (Galaxy XCover 4) (client-side),

Used libraries:
* available in requirements.txt

## Setup

1. Clone git repository.
2. Install required packages:
    ```
    pip install -r requirements.txt
    ```
3. Create file *secrets* in the same directory as settings.py, with following data (without < and >):
    ```
    <secret_key>
    ```
4. Initialize as standard Django application:
    ```
    python manage.py makemigrations
    python manage.py makemigrations qapp
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
    ```
5. Go to admin panel (http://127.0.0.1:8000/admin) and create two groups
   - *dzj* with *qapp all* permissions
   - *prod* with *qapp view*, *qapp add*, *qapp change* permissions
6. In admin panel, create two users and assign them to different groups

This is sufficient to test app in local environment.
If you want to setup application on production environment, uWSGI is recommended.

## Usage

Clear interface is available.
Open http://127.0.0.1:8000/ in your browser to view the main page.
Login with valid username and password.
