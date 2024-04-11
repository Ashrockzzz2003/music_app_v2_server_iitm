# No Auth needed.

from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

import sqlite3

public = Blueprint("public", __name__)

@public.route("/test", methods=["GET"])
def test():
    return make_response(jsonify({"message": "Public API is up and running."}), 200)

@public.route("/language", methods=["GET"])
def getAllLanguages():
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId, languageCode, languageName from languageData WHERE isActive='1'"
        )
        languageData = db_cursor.fetchall()
        db_connection.close()

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        return make_response(jsonify({"data": languageData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getAllLanguages | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@public.route("/language/<int:language_id>", methods=["GET"])
def getLanguageById(language_id):
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId, languageCode, languageName from languageData WHERE languageId = ? AND isActive='1'", (language_id,)
        )
        languageData = db_cursor.fetchall()
        db_connection.close()

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        if languageData == []:
            return make_response(jsonify({"message": "Language not found."}), 404)

        return make_response(jsonify({"data": languageData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getLanguageById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    

@public.route("/genre", methods=["GET"])
def getAllGenres():
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT genreId, genreName, genreDescription from genreData WHERE isActive='1'"
        )
        genreData = db_cursor.fetchall()
        db_connection.close()

        genreData = [dict(zip([key[0] for key in db_cursor.description], genre)) for genre in genreData]

        return make_response(jsonify({"data": genreData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getAllGenres | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@public.route("/genre/<int:genre_id>", methods=["GET"])
def getGenreById(genre_id):
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT genreId, genreName, genreDescription from genreData WHERE genreId = ? AND isActive='1'", (genre_id,)
        )
        genreData = db_cursor.fetchall()
        db_connection.close()

        genreData = [dict(zip([key[0] for key in db_cursor.description], genre)) for genre in genreData]

        if genreData == []:
            return make_response(jsonify({"message": "Genre not found."}), 404)

        return make_response(jsonify({"data": genreData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getGenreById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@public.route("/song/<int:song_id>", methods=["GET"])
def getSongById(song_id):
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * from songData WHERE songId = ? AND isActive='1'", (song_id,)
        )

        songData = db_cursor.fetchone()

        if songData == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        songData = dict(zip([key[0] for key in db_cursor.description], songData))

        if (songData["songAlbumId"] != None):
            db_cursor.execute(
                "SELECT s.songId, s.songName, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, a.albumName, a.albumId, a.albumDescription from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN albumData AS a ON a.albumId = s.songAlbumId WHERE s.songId = ? AND s.isActive='1'", (song_id,)
            )
        else:
            db_cursor.execute(
                "SELECT s.songId, s.songName, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId WHERE s.songId = ? AND s.isActive='1'", (song_id,)
            )

        songData = db_cursor.fetchone()
        db_connection.close()

        if songData == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        songData = dict(zip([key[0] for key in db_cursor.description], songData))

        return make_response(jsonify({"data": songData, "message": "Success"}), 200)

    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getSongById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@public.route("/album/<int:album_id>", methods=["GET"])
def getAlbumById(album_id):
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT a.albumName, a.albumId, a.albumDescription, a.albumReleaseDate, a.albumImageFileExt, a.albumLikesCount, a.albumDislikesCount from albumData AS a WHERE albumId = ? AND isActive='1'", (album_id,)
        )

        albumData = db_cursor.fetchone()

        if albumData == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        albumData = dict(zip([key[0] for key in db_cursor.description], albumData))

        db_cursor.execute(
            "SELECT s.songId, s.songName, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId WHERE s.songAlbumId = ? AND s.isActive='1'", (album_id,)
        )

        songData = db_cursor.fetchall()
        db_connection.close()

        songData = [dict(zip([key[0] for key in db_cursor.description], song)) for song in songData]

        return make_response(jsonify({"data": {"albumData": albumData, "songData": songData}, "message": "Success"}), 200)
    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getAlbumById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@public.route("/album", methods=["GET"])
def getAllAlbums():
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT a.albumName, a.albumId, a.albumDescription, a.albumReleaseDate, a.albumImageFileExt, a.albumLikesCount, a.albumDislikesCount from albumData AS a WHERE isActive='1'"
        )

        albumData = db_cursor.fetchall()

        albumData = [dict(zip([key[0] for key in db_cursor.description], album)) for album in albumData]

        db_connection.close()

        return make_response(jsonify({"data": albumData, "message": "Success"}), 200)
    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getAllAlbums | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)


