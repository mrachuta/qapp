## Project name
qapp - quality assurance app based on Django.

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Using](#using)
* [Thanks](#thanks)

## General info
During work for one of biggest Polish company related to design & production of city cars,
I participated in quality control of these vehicles on all levels. At the beginning, inspections
was made using classic paper sheets. After some projects, managers taken decision that due to
a lot of paper work, there is an special app(environment) necessary. In results of this, an 
Java app (IBM Lotus Notes/Domino environment) was created. Unfortunately, due to very small developers
quantity, only two version was released.
This app is used till 5 years in company but there are many disadvantages:
* app was build in very rare environment (even if it is Java, there are not enough IBM-Domino developers on market)
* code is very complicated - there is a lot of 'if' statements,
* app is not native; it works only inside Lotus Notes Client,
* there is problem with access via VPN (VPN is overloaded; app running only in local network),
* no support for mobile devices,
* the app is insanely slow.

I decided to show some proof-of-concept, that develop and maintain of those type of apps can be easy.
Advantages of qapp:
- app is a Python app (which is only a little bit less popular than Java),
- core for app is Django, which is open-source and very popular framework,
- code is simplified, there are used a lot of django-native mechanisms and solutions,
- app could be run in local network, or as internet service,
- for running as internet-service, there is no VPN necessary,
- support for mobile devices & desktop.

Extra features in qapp which are not supported in original app:
  
* easy adding of new Gate categories (custom ListView),  
* editing of existing Gate(s) object(s) without special permissions 
(permissions can be added in admin panel),  
* multi-adding (possibility to add one Gate to more than one parent object),  
* multi-acceptance (possibility to change status for multiple Gate(s) in one click),  
* possibility to upload photo/file directly from mobile phone during inspection,  
* resizing photos on client-side (save data - on client side and server side),  
* QR-codes compatibility (fast declaration - especially for production department),  
* logs for each Gate object (each action or change i Gate is logged),  
* friendly and fast filtering of objects,  
* current status for logged user: how many Gate objects was declined by QA etc.  
  
## Technologies
* Backend: Python3 + Django,
* Frontend: HTML + CSS,
* Scripts: JavaScript,
* Database: SQLite.

Code was tested on following platforms:
* Ubuntu 16.04.1 LTS (GNU/Linux 2.6.32-openvz-042stab125.5-amd64 x86_64) with Python 3.5.2 (server-side),
* Windows 7 x64 (Opera 58 + Firefox 65) (client-side),
* Android 8.0 (Galaxy S7) (client-side),
* Android 8.1.1 (Galaxy XCover 4) (client-side),

Used libraries:
* available in requirements.txt

## Setup

Online version available at:

http://qapp.thinkbox.pl/

test-user (dzj permissions): 
```
login: test_dzj / pass: djangodzj123
```
test-user (prod permissions): 
```
login: test_prod / pass: djangoprod123
```
For testing on localhost:

1. Clone git repo to localhost.
2. Install required packages.
3. Create file *secrets* in the same directory as settings.py, with following data (without < and >):
    ```
    <secret_key>
    ```
4. Initiate as standard Django-app (superuser, database, migrations etc)

This is sufficient to run Django developer server.  
If you will try to set server as production environment, uWSGI is recommended.


## Using

Clear interface is available. You need to login first.
Access to admin: add <i>/admin</i> after root path.

## Thanks

As always to my girlfriend!
