import psycopg2
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import hashers
from .forms import UserForm


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        create_dict = ({
            'password': hashers.make_password(form.cleaned_data['password']),
            'username': form.cleaned_data['username'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'email': form.cleaned_data['email']
        }, )
        try:
            cur = settings.DATABASE.cursor()
            cur.executemany(
                """
                INSERT INTO "user"("password", "username", "first_name", "last_name", "email") 
                VALUES (%(password)s, %(username)s, %(first_name)s, %(last_name)s, %(email)s)
                """, create_dict)
            settings.DATABASE.commit()
        except psycopg2.Error as e:
            return render(request, 'music/register.html', {'form': form})
        return render(request, 'music/index.html', {'albums': "Hi"})
    return render(request, 'music/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            cur = settings.DATABASE.cursor()
            cur.execute(
                """
                SELECT "user"."id", "user"."username", "user"."password" FROM "user" WHERE "user"."username" = %(username)s
                """, {'username': username})
            settings.DATABASE.commit()
            if not hashers.check_password(password, cur.fetchall()[0][2]):
                return render(request, 'music/login.html')
        except (psycopg2.Error, IndexError) as e:
            return render(request, 'music/login.html')
        return render(request, 'music/index.html')
    return render(request, 'music/login.html')
