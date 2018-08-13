from django import forms


class UserForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(widget=forms.EmailInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class AlbumForm(forms.Form):
    artist = forms.CharField()
    album_title = forms.CharField()
    genre = forms.CharField()
    album_logo = forms.ImageField()


class SongForm(forms.Form):
    song_title = forms.CharField()
    audio_file = forms.FileField()
