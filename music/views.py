import psycopg2
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import hashers
from .forms import UserForm, AlbumForm


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        create_dict = {
            'password': hashers.make_password(form.cleaned_data['password']),
            'username': form.cleaned_data['username'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'email': form.cleaned_data['email']
        }
        try:
            cur = settings.DATABASE.cursor()
            cur.execute(
                """
                INSERT INTO "user"("password", "username", "first_name", "last_name", "email") 
                VALUES (%(password)s, %(username)s, %(first_name)s, %(last_name)s, %(email)s)
                """, create_dict)
            cur.execute(
                """
                SELECT "user"."id", "user"."username",
                "user"."password" FROM "user" WHERE "user"."username" = %(username)s
                """, {'username': create_dict['username']}
            )
            users = cur.fetchall()
            cur.execute(
                """
                SELECT "album"."id", "album"."artist", "album"."album_title",
                 "album"."genre", "album"."album_logo", "album"."is_favorite",
                  "album"."user_id" FROM "album" WHERE "album"."user_id" = %(user_id)s
                """, {'user_id': users[0][0]}
            )
            albums = cur.fetchall()
            album_context = []
            for album in albums:
                album_context.append({
                    'id': album[0],
                    'artist': album[1],
                    'album_title': album[2],
                    'genre': album[3],
                    'album_logo': album[4],
                    'is_favorite': album[5],
                    'user_id': album[6],
                })
        except psycopg2.Error as e:
            settings.DATABASE.rollback()
            return render(request, 'music/register.html', {'form': form, 'error_message': 'Register failed'})
        settings.DATABASE.commit()
        return render(request, 'music/index.html', {
            'albums': album_context,
            'user': {'username': create_dict['username']}
        })
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
                """, {'username': username}
            )
            users = cur.fetchall()
            if not hashers.check_password(password, users[0][2]):
                return render(request, 'music/login.html', {'error_message': 'Login failed!!'})
            cur.execute(
                """
                SELECT "album"."id", "album"."artist", "album"."album_title",
                 "album"."genre", "album"."album_logo", "album"."is_favorite",
                  "album"."user_id" FROM "album" WHERE "album"."user_id" = %(user_id)s
                """, {'user_id': users[0][0]}
            )
            albums = cur.fetchall()
            album_context = []
            for album in albums:
                album_context.append({
                    'id': album[0],
                    'artist': album[1],
                    'album_title': album[2],
                    'genre': album[3],
                    'album_logo': album[4],
                    'is_favorite': album[5],
                    'user_id': album[6],
                })
        except (psycopg2.Error, IndexError) as e:
            settings.DATABASE.rollback()
            return render(request, 'music/login.html', {'error_message': 'Login failed!!'})
        settings.DATABASE.commit()
        return render(request, 'music/index.html', {'albums': album_context, 'user': {'username': users[0][1]}})
    return render(request, 'music/login.html')


def create_album(request, username):
    form = AlbumForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        uploaded_file_url = None
        if request.FILES:
            album_logo_file = request.FILES['album_logo']
            fs = FileSystemStorage()
            filename = fs.save(album_logo_file.name, album_logo_file)
            uploaded_file_url = fs.url(filename)
        try:
            cur = settings.DATABASE.cursor()
            cur.execute(
                """
                SELECT "user"."id" FROM "user" WHERE "user"."username" = %(username)s
                """, {'username': username}
            )
            user_id = cur.fetchall()[0][0]
            album_insert = {
                'artist': form.cleaned_data['artist'],
                'album_title': form.cleaned_data['album_title'],
                'genre': form.cleaned_data['genre'],
                'album_logo': uploaded_file_url,
                'user_id': user_id
            }
            cur.execute(
                """
                INSERT INTO "album"("artist", "album_title", "genre", "album_logo", "user_id")
                VALUES (%(artist)s, %(album_title)s, %(genre)s, %(album_logo)s, %(user_id)s)
                """, album_insert
            )
        except (psycopg2.Error, IndexError) as e:
            print(e)
            settings.DATABASE.rollback()
            return render(request, 'music/create_album.html', {
                'form': form,
                'error_message': 'Album creation failed!!',
                'user': {'username': username}
            })
        settings.DATABASE.commit()
        return render(request, 'music/detail.html', {'user': {'username': username}})
    return render(request, 'music/create_album.html', {'form': form, 'user': {'username': username}})


