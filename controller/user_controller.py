from flask import Blueprint, jsonify, make_response, request
from datetime import datetime

from middleware.tokenValidator import validateToken
from middleware.tokenGenerator import generateToken
from middleware.dataValidator import isValidLoginToken
import sqlite3, os

user = Blueprint("user", __name__)

@user.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "User API is up and running."}), 200)

# Get profile
@user.route("/profile", methods=["GET"])
def getProfile():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] not in range(1, 4):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userFullName, userEmail, userId, userRoleId, userDob, userAccountStatus, createdAt FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Get user Watch History

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData as u on u.userId = s.createdBy WHERE s.isActive='1' AND s.songId IN (SELECT songId FROM userHistory WHERE userId = ?)",
            (userId,),
        )

        user_songs = db_cursor.fetchall()
        db_connection.close()

        user_songs = [dict(zip([key[0] for key in db_cursor.description], song)) for song in user_songs]

        return make_response(
            jsonify({"message": "User found.", "data": user_data, "songs": user_songs}), 200
        )

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | getProfile | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)


# Register as a creator
@user.route("/i-wanna-be-creator", methods=["POST"])
def iWannaBeACreator():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)

        if user_data["userRoleId"] == 2:
            return make_response(
                jsonify({"message": "You are already a creator."}), 400
            )

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE userData SET userRoleId = 2 WHERE userId = ?",
            (userId,),
        )
        db_connection.commit()

        db_cursor.execute(
            "SELECT userFullName, userEmail, userId, userRoleId, userDob, userAccountStatus, createdAt FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        token = generateToken(
            {
                "userId": user_data["userId"],
                "userAccountStatus": user_data["userAccountStatus"],
                "userRoleId": user_data["userRoleId"],
            }
        )

        return make_response(
            jsonify(
                {"message": "You are now a creator.", "data": user_data, "token": token}
            ),
            200,
        )

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | iWannaBeACreator | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# PlayList API
# Create Playlist
@user.route("/playlist/create", methods=["POST"])
def createNewPlaylist():
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)

        # Validate Request

        # playlistName, hasImage, isPublic
        if (
            "playlistName" not in data
            or "hasImage" not in data
            or "isPublic" not in data
        ):
            return make_response(jsonify({"message": "Missing required fields."}), 400)

        if (
            type(data["playlistName"]) != str
            or type(data["hasImage"]) != str
            or type(data["isPublic"]) != str
        ):
            return make_response(jsonify({"message": "Invalid data type."}), 400)

        if data["hasImage"] not in ["0", "1"] or data["isPublic"] not in ["0", "1"]:
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if len(data["playlistName"]) == 0:
            return make_response(jsonify({"message": "Invalid data."}), 400)

        playlistName = data["playlistName"]
        hasImage = data["hasImage"]
        isPublic = data["isPublic"]

        playlistDescription = (
            data["playlistDescription"] if "playlistDescription" in data else None
        )
        playlistImageFileExt = (
            data["playlistImageFileExt"] if "playlistImageFileExt" in data else None
        )

        # Check if another playlist with same name exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE createdBy = ? AND playlistName = ?",
            (userId, playlistName),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data != None:
            # Please choose a different playlist name as message
            return make_response(
                jsonify({"message": "Please choose a different playlist name! Sorry!"}),
                400,
            )

        # Check if image is there if hasImage is 1
        if hasImage == "1":
            if "playlistImage" not in request.files:
                return make_response(
                    jsonify({"message": "Missing required fields."}), 400
                )

            playlistImage = request.files["playlistImage"]
            if playlistImage.filename == "":
                return make_response(
                    jsonify({"message": "Missing required fields."}), 400
                )

            playlistImageFileExt = playlistImage.filename.split(".")[-1]

            if playlistImageFileExt != "png":
                return make_response(
                    jsonify({"message": "Invalid file extension."}), 400
                )

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO playlistData (playlistName, playlistDescription, hasImage, playlistImageFileExt, playlistLikesCount, playlistDislikesCount, isPublic, isActive, createdBy, lastUpdatedBy) VALUES (?, ?, ?, ?, 0, 0, ?, 1, ?, ?)",
            (
                playlistName,
                playlistDescription,
                hasImage,
                playlistImageFileExt,
                isPublic,
                userId,
                userId,
            ),
        )

        db_connection.commit()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE createdBy = ? AND playListName = ? ORDER BY createdAt DESC LIMIT 1",
            (userId, playlistName),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        playlist_data = dict(
            zip([key[0] for key in db_cursor.description], playlist_data)
        )

        # Save image if hasImage is 1

        if hasImage == "1":
            playlistImage.save(
                f"play_list/{playlist_data['playlistId']}.{playlistImageFileExt}"
            )

        return make_response(
            jsonify(
                {"message": "Playlist created successfully.", "data": playlist_data}
            ),
            200,
        )

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | createNewPlaylist | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Update Playlist
@user.route("/playlist/<int:playlist_id>/update", methods=["POST"])
def updatePlayList(playlist_id):
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)
        
        data = request.get_json()

        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)

        # Validate Request

        # playlistName, hasImage, isPublic
        if (
            "playlistName" not in data
            or "hasImage" not in data
            or "isPublic" not in data
        ):
            return make_response(jsonify({"message": "Missing required fields."}), 400)

        if (
            type(data["playlistName"]) != str
            or type(data["hasImage"]) != str
            or type(data["isPublic"]) != str
        ):
            return make_response(jsonify({"message": "Invalid data type."}), 400)

        if data["hasImage"] not in ["0", "1"] or data["isPublic"] not in ["0", "1"]:
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if len(data["playlistName"]) == 0:
            return make_response(jsonify({"message": "Invalid data."}), 400)

        playlistName = data["playlistName"]
        hasImage = data["hasImage"]
        isPublic = data["isPublic"]

        playlistDescription = (
            data["playlistDescription"] if "playlistDescription" in data else None
        )
        playlistImageFileExt = (
            data["playlistImageFileExt"] if "playlistImageFileExt" in data else None
        )

        # Check is playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)

        playlist_data = dict(
            zip([key[0] for key in db_cursor.description], playlist_data)
        )

        if playlist_data["createdBy"] != userId and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Check if image is there if hasImage is 1

        if hasImage == "1":
            if "playlistImage" not in request.files:
                return make_response(
                    jsonify({"message": "Missing required fields."}), 400
                )

            playlistImage = request.files["playlistImage"]
            if playlistImage.filename == "":
                return make_response(
                    jsonify({"message": "Missing required fields."}), 400
                )

            playlistImageFileExt = playlistImage.filename.split(".")[-1]

            if playlistImageFileExt != "png":
                return make_response(
                    jsonify({"message": "Invalid file extension."}), 400
                )

        # Check if another playlist with same name exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistName = ? AND playlistId != ?",
            (playlistName, playlist_id),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data != None:
            # Please choose a different playlist name as message
            return make_response(
                jsonify({"message": "Please choose a different playlist name! Sorry!"}),
                400,
            )

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE playlistData SET playlistName = ?, playlistDescription = ?, hasImage = ?, playlistImageFileExt = ?, isPublic = ?, lastUpdatedBy = ? WHERE playlistId = ?",
            (
                playlistName,
                playlistDescription,
                hasImage,
                playlistImageFileExt,
                isPublic,
                userId,
                playlist_id,
            ),
        )

        db_connection.commit()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        playlist_data = dict(
            zip([key[0] for key in db_cursor.description], playlist_data)
        )

        # Save image if hasImage is 1

        if hasImage == "1":
            playlistImage.save(
                f"play_list/{playlist_data['playlistId']}.{playlistImageFileExt}"
            )

        return make_response(
            jsonify(
                {"message": "Playlist updated successfully.", "data": playlist_data}
            ),
            200,
        )

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | updatePlayList | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Add song to playlist
@user.route("/playlist/<int:playlist_id>/add-song/<int:song_id>", methods=["POST"])
def addSong(playlist_id, song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and user_data["userRoleId"] != 1 :
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ? AND isActive = '1'",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is already in playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistSongData WHERE playlistId = ? AND songId = ?",
            (playlist_id, song_id),
        )

        playlist_song_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_song_data != None:
            return make_response(jsonify({"message": "Song already in playlist."}), 400)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO playlistSongData (playlistId, songId) VALUES (?, ?)",
            (playlist_id, song_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song added to playlist."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | addSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Remove song from playlist
@user.route("/playlist/<int:playlist_id>/remove-song/<int:song_id>", methods=["POST"])
def removeSongFromPlaylist(playlist_id, song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")

        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ? AND isActive = '1'",
            (song_id,),
        )

        song_data = db_cursor.fetchone()

        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is already in playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistSongData WHERE playlistId = ? AND songId = ?",
            (playlist_id, song_id),
        )

        playlist_song_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_song_data == None:
            return make_response(jsonify({"message": "Song not in playlist."}), 400)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "DELETE FROM playlistSongData WHERE playlistId = ? AND songId = ?",
            (playlist_id, song_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song removed from playlist."}), 200)
    
    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | removeSongFromPlaylist | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/playlist", methods=["GET"])
def getPlaylists():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")

        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE createdBy = ?",
            (userId,),
        )

        playlist_data = db_cursor.fetchall()
        db_connection.close()

        playlist_data = [dict(zip([key[0] for key in db_cursor.description], playlist)) for playlist in playlist_data]

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT playlistId, playlistName, playlistDescription, isPublic, userFullName from playlistData JOIN userData ON userData.userId = playlistData.createdBy WHERE createdBy != ? AND isPublic = '1'",
            (userId,),
        )

        public_playlists = db_cursor.fetchall()
        db_connection.close()

        public_playlists = [dict(zip([key[0] for key in db_cursor.description], playlist)) for playlist in public_playlists]

        return make_response(jsonify({"message": "Playlists found.", "data": playlist_data, "public": public_playlists}), 200)
        

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | getPlaylists | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/playlist/<int:playlist_id>", methods=["GET"])
def getPlaylistById(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and playlist_data["isPublic"] != "1" and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData as u on u.userId = s.createdBy WHERE s.isActive='1' AND s.songId IN (SELECT songId FROM playlistSongData WHERE playlistId = ?)",
            (playlist_id,),
        )

        playlist_songs = db_cursor.fetchall()
        db_connection.close()

        playlist_songs = [dict(zip([key[0] for key in db_cursor.description], song)) for song in playlist_songs]

        return make_response(jsonify({"message": "Playlist found.", "data": playlist_data, "songs": playlist_songs}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | getPlaylistById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/playlist/<int:playlist_id>/like", methods=["POST"])
def likePlaylist(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        

        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        # check if user has already liked the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistLikeDislikeData WHERE userId = ? AND playlistId = ? AND isLike = '1'",
            (userId, playlist_id),
        )

        like_data = db_cursor.fetchone()
        db_connection.close()

        if like_data != None:
            return make_response(jsonify({"message": "You have already liked the playlist."}), 400)
        
        # check if user has already disliked the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistLikeDislikeData WHERE userId = ? AND playlistId = ? AND isLike = '0'",
            (userId, playlist_id),
        )

        dislike_data = db_cursor.fetchone()
        db_connection.close()

        if dislike_data != None:
            # Update the dislike to like

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "UPDATE playlistLikeDislikeData SET isLike = '1' WHERE userId = ? AND playlistId = ?",
                (userId, playlist_id),
            )

            db_cursor.execute(
                "UPDATE playlistData SET playlistLikesCount = playlistLikesCount + 1, playlistDislikesCount = playlistDislikesCount - 1 WHERE playlistId = ?",
                (playlist_id,),
            )

            db_connection.commit()

            db_connection.close()

            return make_response(jsonify({"message": "Playlist liked."}), 200)
        
        # Like the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO playlistLikeDislikeData (userId, playlistId, isLike) VALUES (?, ?, '1')",
            (userId, playlist_id),
        )

        db_cursor.execute(
            "UPDATE playlistData SET playlistLikesCount = playlistLikesCount + 1 WHERE playlistId = ?",
            (playlist_id,),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Playlist liked."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | likePlaylist | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/playlist/<int:playlist_id>/dislike", methods=["POST"])
def dislikePlaylist(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        

        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        # check if user has already disliked the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistLikeDislikeData WHERE userId = ? AND playlistId = ? AND isLike = '0'",
            (userId, playlist_id),
        )

        dislike_data = db_cursor.fetchone()
        db_connection.close()

        if dislike_data != None:
            return make_response(jsonify({"message": "You have already disliked the playlist."}), 400)
        
        # check if user has already liked the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistLikeDislikeData WHERE userId = ? AND playlistId = ? AND isLike = '1'",
            (userId, playlist_id),
        )

        like_data = db_cursor.fetchone()
        db_connection.close()

        if like_data != None:
            # Update the like to dislike

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "UPDATE playlistLikeDislikeData SET isLike = '0' WHERE userId = ? AND playlistId = ?",
                (userId, playlist_id),
            )

            db_cursor.execute(
                "UPDATE playlistData SET playlistLikesCount = playlistLikesCount - 1, playlistDislikesCount = playlistDislikesCount + 1 WHERE playlistId = ?",
                (playlist_id,),
            )

            db_connection.commit()

            db_connection.close()

            return make_response(jsonify({"message": "Playlist disliked."}), 200)
        
        # Dislike the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO playlistLikeDislikeData (userId, playlistId, isLike) VALUES (?, ?, '0')",
            (userId, playlist_id),
        )

        db_cursor.execute(
            "UPDATE playlistData SET playlistDislikesCount = playlistDislikesCount + 1 WHERE playlistId = ?",
            (playlist_id,),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Playlist disliked."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | dislikePlaylist | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/playlist/<int:playlist_id>/delete", methods=["POST"])
def deletePlaylist(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        

        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Delete the playlist

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "DELETE FROM playlistLikeDislikeData WHERE playlistId = ?",
            (playlist_id,),
        )

        db_cursor.execute(
            "DELETE FROM playlistSongData WHERE playlistId = ?",
            (playlist_id,),
        )

        db_cursor.execute(
            "DELETE FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        db_connection.commit()
        db_connection.close()

        # Delete the image if exists

        if playlist_data["hasImage"] == "1":
            os.remove(f"play_list/{playlist_data['playlistId']}.{playlist_data['playlistImageFileExt']}")

        return make_response(jsonify({"message": "Playlist deleted."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | deletePlaylist | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@user.route("/playlist/<int:playlist_id>/toggle-access", methods=["POST"])
def togglePlayListAccess(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Check if playlist exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Toggle the access

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        if playlist_data["isPublic"] == "1":
            db_cursor.execute(
                "UPDATE playlistData SET isPublic = '0' WHERE playlistId = ?",
                (playlist_id,),
            )
        else:
            db_cursor.execute(
                "UPDATE playlistData SET isPublic = '1' WHERE playlistId = ?",
                (playlist_id,),
            )

        db_connection.commit()

        db_connection.close()

        return make_response(jsonify({"message": "Playlist access toggled."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | togglePlayListAccess | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@user.route("/playlist/<int:playlist_id>/not-in-playlist", methods=["GET"])
def getSongsNotInPlaylist(playlist_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM playlistData WHERE playlistId = ?",
            (playlist_id,),
        )

        playlist_data = db_cursor.fetchone()
        db_connection.close()

        if playlist_data == None:
            return make_response(jsonify({"message": "Playlist not found."}), 404)
        
        playlist_data = dict(zip([key[0] for key in db_cursor.description], playlist_data))

        if playlist_data["createdBy"] != userId and playlist_data["isPublic"] != "1" and user_data["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData as u on u.userId = s.createdBy WHERE s.isActive='1' AND s.songId NOT IN (SELECT songId FROM playlistSongData WHERE playlistId = ?)",
            (playlist_id,),
        )

        playlist_songs = db_cursor.fetchall()
        db_connection.close()

        playlist_songs = [dict(zip([key[0] for key in db_cursor.description], song)) for song in playlist_songs]

        return make_response(jsonify({"message": "Playlist found.", "data": playlist_data, "songs": playlist_songs}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | getPlaylistById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Song API

@user.route("/song/<int:song_id>/like", methods=["POST"])
def likeSong(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        

        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ? AND isActive = '1'",
            (song_id,),
        )

        song_data = db_cursor.fetchone()

        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # check if user has already liked the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songLikeDislikeData WHERE userId = ? AND songId = ? AND isLike = '1'",
            (userId, song_id),
        )

        like_data = db_cursor.fetchone()
        db_connection.close()

        if like_data != None:
            return make_response(jsonify({"message": "You have already liked the song."}), 400)
        
        # check if user has already disliked the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songLikeDislikeData WHERE userId = ? AND songId = ? AND isLike = '0'",
            (userId, song_id),
        )

        dislike_data = db_cursor.fetchone()
        db_connection.close()

        if dislike_data != None:
            # Update the dislike to like

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "UPDATE songLikeDislikeData SET isLike = '1' WHERE userId = ? AND songId = ?",
                (userId, song_id),
            )

            db_cursor.execute(
                "UPDATE songData SET likesCount = likesCount + 1, dislikesCount = dislikesCount - 1 WHERE songId = ?",
                (song_id,),
            )

            db_connection.commit()

            db_connection.close()

            return make_response(jsonify({"message": "Song liked."}), 200)
        
        # Like the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO songLikeDislikeData (userId, songId, isLike) VALUES (?, ?, '1')",
            (userId, song_id),
        )

        db_cursor.execute(
            "UPDATE songData SET likesCount = likesCount + 1 WHERE songId = ?",
            (song_id,),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song liked."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | likeSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@user.route("/song/<int:song_id>/dislike", methods=["POST"])
def dislikeSong(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        

        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ? AND isActive = '1'",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # check if user has already disliked the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songLikeDislikeData WHERE userId = ? AND songId = ? AND isLike = '0'",
            (userId, song_id),
        )

        dislike_data = db_cursor.fetchone()

        db_connection.close()

        if dislike_data != None:
            return make_response(jsonify({"message": "You have already disliked the song."}), 400)
        
        # check if user has already liked the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songLikeDislikeData WHERE userId = ? AND songId = ? AND isLike = '1'",
            (userId, song_id),
        )

        like_data = db_cursor.fetchone()

        db_connection.close()

        if like_data != None:
            # Update the like to dislike

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "UPDATE songLikeDislikeData SET isLike = '0' WHERE userId = ? AND songId = ?",
                (userId, song_id),
            )

            db_cursor.execute(
                "UPDATE songData SET likesCount = likesCount - 1, dislikesCount = dislikesCount + 1 WHERE songId = ?",
                (song_id,),
            )

            db_connection.commit()

            db_connection.close()

            return make_response(jsonify({"message": "Song disliked."}), 200)
        
        # Dislike the song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO songLikeDislikeData (userId, songId, isLike) VALUES (?, ?, '0')",
            (userId, song_id),
        )

        db_cursor.execute(
            "UPDATE songData SET dislikesCount = dislikesCount + 1 WHERE songId = ?",
            (song_id,),
        )

        db_connection.commit()

        db_connection.close()

        return make_response(jsonify({"message": "Song disliked."}), 200)

    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | dislikeSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@user.route("/song/search", methods=["GET"])
def songSearch():
    # Search by songName, songGenre, songArtist, songLanguage, songAlbum
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)
        
        # Get liked songs

        song_like_dislike_dict = {}

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songLikeDislikeData WHERE userId = ?",
            (userId,),
        )

        like_dislike_data = db_cursor.fetchall()
        db_connection.close()

        like_dislike_data = [dict(zip([key[0] for key in db_cursor.description], song)) for song in like_dislike_data]

        for song in like_dislike_data:
            song_like_dislike_dict[song["songId"]] = song["isLike"]

        if not request.args.get("q") and not request.args.get("g") and not request.args.get("l"):
            # Select random 20 songs
            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData as u on u.userId = s.createdBy WHERE s.isActive='1' ORDER BY RANDOM() LIMIT 20"
            )

            songData = db_cursor.fetchall()
            db_connection.close()

            songData = [dict(zip([key[0] for key in db_cursor.description], song)) for song in songData]

            for song in songData:
                if song["songId"] in song_like_dislike_dict:
                    song["isLike"] = song_like_dislike_dict[song["songId"]]
                else:
                    song["isLike"] = "-1"

            return make_response(jsonify({"data": songData, "message": "Success"}), 200)


        search_query = request.args.get("q") if request.args.get("q") else ""
        genre_id = '0'
        language_id = '0'

        if request.args.get("g"):
            genre_id = request.args.get("g")

        if request.args.get("l"):
            language_id = request.args.get("l")

        search_query = str(search_query).lower()

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        if (genre_id != '0' and language_id != '0'):
            db_cursor.execute(
                "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData AS u ON u.userId = s.createdBy WHERE (lower(s.songName) LIKE ? OR lower(u.userFullName) LIKE ? OR lower(g.genreName) LIKE ? OR lower(l.languageName) LIKE ?) AND s.isActive='1' AND s.songGenreId = ? AND s.songLanguageId = ?", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", genre_id, language_id)
            )
        elif (genre_id != '0'):
            db_cursor.execute(
                "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData AS u ON u.userId = s.createdBy WHERE (lower(s.songName) LIKE ? OR lower(u.userFullName) LIKE ? OR lower(g.genreName) LIKE ? OR lower(l.languageName) LIKE ?) AND s.isActive='1' AND s.songGenreId = ?", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", genre_id)
            )
        elif (language_id != '0'):
            db_cursor.execute(
                "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData AS u ON u.userId = s.createdBy WHERE (lower(s.songName) LIKE ? OR lower(u.userFullName) LIKE ? OR lower(g.genreName) LIKE ? OR lower(l.languageName) LIKE ?) AND s.isActive='1' AND s.songLanguageId = ?", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", language_id)
            )
        else:
            db_cursor.execute(
                "SELECT s.songId, s.songPlaysCount, s.songName, s.songDescription, s.songDuration, l.languageId, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, s.songAlbumId, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData AS u ON u.userId = s.createdBy WHERE (lower(s.songName) LIKE ? OR lower(u.userFullName) LIKE ? OR lower(g.genreName) LIKE ? OR lower(l.languageName) LIKE ?) AND s.isActive='1'", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",)
            )

        songData = db_cursor.fetchall()
        db_connection.close()

        songData = [dict(zip([key[0] for key in db_cursor.description], song)) for song in songData]

        for song in songData:
            if song["songId"] in song_like_dislike_dict:
                song["isLike"] = song_like_dislike_dict[song["songId"]]
            else:
                song["isLike"] = "-1"

        return make_response(jsonify({"data": songData, "message": "Success"}), 200)
    
    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | songSearch | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    

@user.route("/song/<int:song_id>/play", methods=["POST"])
def playSong(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if decryptedToken["userRoleId"] != 3 and decryptedToken["userRoleId"] != 2 and decryptedToken["userRoleId"] != 1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)

        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != "1":
            return make_response(jsonify({"message": "Your account is blocked."}), 401)

        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ? AND isActive = '1'",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # insert into user history

        # userHistory

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        
        db_cursor.execute(
            "SELECT * FROM userHistory WHERE userId = ? AND songId = ?",
            (userId, song_id),
        )

        user_history_data = db_cursor.fetchone()

        if user_history_data == None:
            db_cursor.execute(
                "INSERT INTO userHistory (userId, songId) VALUES (?, ?)",
                (userId, song_id),
            )
        else:
            db_cursor.execute(
                "UPDATE userHistory SET noOfPlays = noOfPlays + 1 WHERE userId = ? AND songId = ?",
                (userId, song_id),
            )

        db_connection.commit()
        db_connection.close()

        # Update the song plays count

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE songData SET songPlaysCount = songPlaysCount + 1 WHERE songId = ?",
            (song_id,),
        )

        db_connection.commit()
        db_connection.close()

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        if (song_data["songAlbumId"] != None):
            db_cursor.execute(
                "SELECT s.songId, s.songName, s.songPlaysCount, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, a.albumName, a.albumId, a.albumDescription, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN albumData AS a ON a.albumId = s.songAlbumId JOIN userData as u on u.userId = s.createdBy WHERE s.songId = ? AND s.isActive='1'", (song_id,)
            )
        else:
            db_cursor.execute(
                "SELECT s.songId, s.songName, s.songPlaysCount, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.likesCount, s.dislikesCount, s.songAudioFileExt, s.songImageFileExt, s.songLanguageId, l.languageName, l.languageCode, s.songGenreId, g.genreName, g.genreDescription, u.userFullName, u.userId from songData AS s JOIN languageData AS l ON l.languageId = s.songLanguageId JOIN genreData AS g ON g.genreId = s.songGenreId JOIN userData as u on u.userId = s.createdBy WHERE s.songId = ? AND s.isActive='1'", (song_id,)
            )

        songData = db_cursor.fetchone()
        db_connection.close()

        songData = dict(zip([key[0] for key in db_cursor.description], songData))

        # Check if the song is liked by the user

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT isLike FROM songLikeDislikeData WHERE userId = ? AND songId = ?",
            (userId, song_id),
        )

        like_data = db_cursor.fetchone()
        db_connection.close()

        if like_data != None:
            songData["isLike"] = like_data[0]
        else:
            songData["isLike"] = "-1"


        return make_response(jsonify({"data": songData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | playSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

