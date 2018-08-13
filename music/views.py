import psycopg2
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import hashers
from .forms import UserForm, AlbumForm, SongForm


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
                RETURNING "album"."id"
                """, album_insert
            )
            new_album_id = cur.fetchall()[0][0]
            cur.execute(
                """
                SELECT "album"."id", "album"."artist", "album"."album_title", 
                "album"."genre", "album"."album_logo", "album"."is_favorite",
                 "album"."user_id" FROM "album" WHERE "album"."id" = %(album_id)s
                """, {'album_id': new_album_id}
            )
            album = cur.fetchall()[0]
            album = {
                'id': album[0],
                'user_id': album[6],
                'artist': album[1],
                'album_title': album[2],
                'genre': album[3],
                'album_logo': album[4],
                'is_favorite': album[5],
            }
            cur.execute(
                """
                SELECT "song"."id", "song"."album_id", "song"."song_title", "song"."audio_file",
                "song"."is_favorite" FROM "song" WHERE "song"."album_id" = %(album_id)s
                """, {'album_id': new_album_id}
            )
            songs = cur.fetchall()
            album['song_set'] = []
            for song in songs:
                album['song_set'].append({
                    'id': song[0],
                    'album_id': song[1],
                    'song_title': song[2],
                    'audio_file': song[3],
                    'is_favorite': song[4],
                })
        except (psycopg2.Error, IndexError) as e:
            settings.DATABASE.rollback()
            return render(request, 'music/create_album.html', {
                'form': form,
                'error_message': 'Album creation failed!!',
                'user': {'username': username}
            })
        settings.DATABASE.commit()
        return render(request, 'music/detail.html', {'album': album, 'user': {'username': username}})
    return render(request, 'music/create_album.html', {'form': form, 'user': {'username': username}})


def create_song(request, username, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    try:
        cur = settings.DATABASE.cursor()
        cur.execute(
            """
            SELECT "album"."id", "album"."user_id", "album"."artist",
            "album"."album_title", "album"."genre", "album"."album_logo",
            "album"."is_favorite" FROM "album" WHERE "album"."id" = %(album_id)s
            """, {'album_id': album_id}
        )
        album = cur.fetchall()[0]
        album = {
            'id': album[0],
            'user_id': album[1],
            'artist': album[2],
            'album_title': album[3],
            'genre': album[4],
            'album_logo': album[5],
            'is_favorite': album[6],
        }
    except (psycopg2.Error, IndexError) as e:
        settings.DATABASE.rollback()
        raise Http404
    if form.is_valid():
        uploaded_file_url = None
        if request.FILES:
            audio_file = request.FILES['audio_file']
            fs = FileSystemStorage()
            filename = fs.save(audio_file.name, audio_file)
            uploaded_file_url = fs.url(filename)
        try:
            cur.execute(
                """
                INSERT INTO "song"("album_id", "song_title", "audio_file")
                VALUES (%(album_id)s, %(song_title)s, %(audio_file)s)
                """, {
                    'album_id': album_id,
                    'song_title': form.cleaned_data['song_title'],
                    'audio_file': uploaded_file_url
                }
            )
            cur.execute(
                """
                SELECT "song"."id", "song"."album_id", "song"."song_title", "song"."audio_file",
                "song"."is_favorite" FROM "song" WHERE "song"."album_id" = %(album_id)s
                """, {'album_id': album_id}
            )
            songs = cur.fetchall()
            album['song_set'] = []
            for song in songs:
                album['song_set'].append({
                    'id': song[0],
                    'album_id': song[1],
                    'song_title': song[2],
                    'audio_file': song[3],
                    'is_favorite': song[4],
                })
        except (psycopg2.Error, IndexError) as e:
            settings.DATABASE.rollback()
            return render(request, 'music/create_song.html', {
                'form': form,
                'user': {'username': username},
                'album': album,
                'error_message': 'Failed to create song!!!',
            })
        settings.DATABASE.commit()
        return render(request, 'music/detail.html', {'album': album, 'user': {'username': username}})
    return render(request, 'music/create_song.html', {'form': form, 'user': {'username': username}, 'album': album})


def detail(request, username, album_id):
    try:
        cur = settings.DATABASE.cursor()
        cur.execute(
            """
            SELECT "album"."id", "album"."artist", "album"."album_title", 
            "album"."genre", "album"."album_logo", "album"."is_favorite",
             "album"."user_id" FROM "album" WHERE "album"."id" = %(album_id)s
            """, {'album_id': album_id}
        )
        album = cur.fetchall()[0]
        album = {
            'id': album[0],
            'user_id': album[6],
            'artist': album[1],
            'album_title': album[2],
            'genre': album[3],
            'album_logo': album[4],
            'is_favorite': album[5],
        }
        cur.execute(
            """
            SELECT "song"."id", "song"."album_id", "song"."song_title", "song"."audio_file",
            "song"."is_favorite" FROM "song" WHERE "song"."album_id" = %(album_id)s
            """, {'album_id': album_id}
        )
        songs = cur.fetchall()
        album['song_set'] = []
        for song in songs:
            album['song_set'].append({
                'id': song[0],
                'album_id': song[1],
                'song_title': song[2],
                'audio_file': song[3],
                'is_favorite': song[4],
            })
        settings.DATABASE.commit()
        return render(request, 'music/detail.html', {'album': album, 'user': {'username': username}})
    except (psycopg2.Error, IndexError) as e:
        raise Http404


def songs(request, username, filter_by):
    try:
        cur = settings.DATABASE.cursor()
        if filter_by == 'favorites':
            cur.execute(
                """
                SELECT "song"."id", "song"."song_title", "song"."audio_file", 
                "album"."artist", "album"."id", "album"."album_title", "album"."album_logo" 
                FROM "song", "album", "user"
                WHERE "user"."username" = %(username)s AND "user"."id" = "album"."user_id"
                AND "album"."id" = "song"."album_id" AND "song"."is_favorite" = TRUE
                """, {'username': username}
            )
        elif filter_by == 'all':
            cur.execute(
                """
                SELECT "song"."id", "song"."song_title", "song"."audio_file", 
                "album"."artist", "album"."id", "album"."album_title", "album"."album_logo"
                FROM "song", "album", "user"
                WHERE "user"."username" = %(username)s AND "user"."id" = "album"."user_id"
                AND "album"."id" = "song"."album_id"
                """, {'username': username}
            )
        else:
            raise Http404
        result = cur.fetchall()
        context = []
        for song in result:
            context.append({
                'id': song[0],
                'song_title': song[1],
                'audio_file': song[2],
                'album': {
                    'artist': song[3],
                    'id': song[4],
                    'album_title': song[5],
                    'album_logo': song[6]
                }
            })
        return render(request, 'music/songs.html', {
            'song_list': context,
            'filter_by': filter_by,
            'user': {'username': username, },
        })
    except (psycopg2.Error, IndexError) as e:
        raise Http404
