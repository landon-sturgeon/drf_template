## Basic Django Backend for Future Projects ##

I've implemented a pretty basic Django backend using the Django REST Framework for future projects.

The main goal was to stop repeating backend development as much as I could, and with this template, user authentication and basic object relationships, filtering, image uploads, and unit testing can quickly be brought up.

### Dependencies ###

Package Dependencies can be seen in the ```requirements.txt``` file. Besides that:
<ul>
    <li>postgresql-client</li>
    <li>jpeg-dev</li>
    <li>Docker Desktop</li>
</ul>

**Start Up**
<ol>
<li>Create a virtual environment</li>
<li>clone the repo to the folder you want</li>
<li>cd into the repo and "pip install -r requirements.txt"</li>
<li>Make sure your Docker Desktop is running</li>
<li>"docker-compose build"</li>
<li>"docker-compose run --rm sh -c "python manage.py makemigrations"</li>
<li>"docker-compose up"</li>
<li>Go to your favorite browser and enter "127.0.0.1:8000/api/"</li>
</ol>

The above address with show what other links you can go to. The only endpoint that is publicly available is the ```127.0.0.1:8000/api/user/create/```, where you'll have to create a new user. From there go to ```127.0.0.1:8000/api/user/token/``` and enter the username and password you just created to get your authentication token. You'll need this token to gain access to the rest of the API endpoints.

I enjoy using [ModHeader](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en) for the token header, but you can use your own. If you do use ModHeader, you can set up the token authentication like so:

 ![ModHeader Auth Token](modheader_auth_token.PNG?raw=True "ModHeader Auth Token")