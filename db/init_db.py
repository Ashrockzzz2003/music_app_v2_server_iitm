import sqlite3
from datetime import datetime

init_script = """
DROP TABLE IF EXISTS "playlistSongData";
DROP TABLE IF EXISTS "playlistLikeDislikeData";
DROP TABLE IF EXISTS "playlistData";
DROP TABLE IF EXISTS "albumLikeDislikeData";
DROP TABLE IF EXISTS "albumSongData";
DROP TABLE IF EXISTS "albumData";
DROP TABLE IF EXISTS "userHistory";
DROP TABLE IF EXISTS "songLikeDislikeData";
DROP TABLE IF EXISTS "songArtistData";
DROP TABLE IF EXISTS "songData";
DROP TABLE IF EXISTS "languageData";
DROP TABLE IF EXISTS "genreData";
DROP TABLE IF EXISTS "userFollows";
DROP TABLE IF EXISTS "userData";
DROP TABLE IF EXISTS "userRole";
CREATE TABLE IF NOT EXISTS "userRole" (
    "roleId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "roleName" VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS "userData" (
    "userId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userFullName" VARCHAR(255) NOT NULL,
    "userEmail" VARCHAR(255) NOT NULL UNIQUE,
    "userPassword" VARCHAR(255) NOT NULL,
    "userDob" VARCHAR(255) NOT NULL,
    "userGender" CHAR(1) NOT NULL,
    "userAccountStatus" CHAR(1) NOT NULL,
    "userRoleId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("userRoleId") REFERENCES "userRole"("roleId"),
    CHECK ("userGender" IN ('M', 'F', 'O')),
    CHECK ("userAccountStatus" IN ('0', '1', '2'))
);
CREATE TABLE IF NOT EXISTS "userFollows" (
    "userId" INTEGER NOT NULL,
    "followsUserId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("followsUserId") REFERENCES "userData"("userId"),
    PRIMARY KEY ("userId", "followsUserId")
);
CREATE TABLE IF NOT EXISTS "genreData" (
    "genreId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "genreName" VARCHAR(255) NOT NULL,
    "genreDescription" VARCHAR(255) NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "languageData" (
    "languageId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "languageName" VARCHAR(255) NOT NULL,
    "languageDescription" VARCHAR(255) NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "songData" (
    "songId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "songName" VARCHAR(255) NOT NULL,
    "songDescription" VARCHAR(255) NULL,
    "songDuration" INTEGER NOT NULL,
    "songReleaseDate" TEXT NOT NULL,
    "songLyrics" TEXT NULL,
    "songAudioFileExt" VARCHAR(10) NOT NULL,
    "songImageFileExt" VARCHAR(10) NOT NULL,
    "songGenreId" INTEGER NOT NULL,
    "songLanguageId" INTEGER NOT NULL,
    "songAlbumId" INTEGER NULL,
    "likesCount" INTEGER NOT NULL,
    "dislikesCount" INTEGER NOT NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("songGenreId") REFERENCES "genreData"("genreId"),
    FOREIGN KEY ("songLanguageId") REFERENCES "languageData"("languageId"),
    FOREIGN KEY ("songAlbumId") REFERENCES "albumData"("albumId"),
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "songArtistData" (
    "songId" INTEGER NOT NULL,
    "artistId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    FOREIGN KEY ("artistId") REFERENCES "artistData"("artistId"),
    PRIMARY KEY ("songId", "artistId")
);
CREATE TABLE IF NOT EXISTS "songLikeDislikeData" (
    "userId" INTEGER NOT NULL,
    "songId" INTEGER NOT NULL,
    "isLike" CHAR(1) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    PRIMARY KEY ("userId", "songId")
);
CREATE TABLE IF NOT EXISTS "userHistory" (
    "userId" INTEGER NOT NULL,
    "songId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    PRIMARY KEY ("userId", "songId")
);
CREATE TABLE IF NOT EXISTS "albumData" (
    "albumId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "albumName" VARCHAR(255) NOT NULL,
    "albumDescription" VARCHAR(255) NULL,
    "albumReleaseDate" TEXT NOT NULL,
    "albumImageFileExt" VARCHAR(10) NOT NULL,
    "albumLikesCount" INTEGER NOT NULL,
    "albumDislikesCount" INTEGER NOT NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "albumSongData" (
    "albumId" INTEGER NOT NULL,
    "songId" INTEGER NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("albumId") REFERENCES "albumData"("albumId"),
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    PRIMARY KEY ("albumId", "songId")
);
CREATE TABLE IF NOT EXISTS "albumLikeDislikeData" (
    "userId" INTEGER NOT NULL,
    "albumId" INTEGER NOT NULL,
    "isLike" CHAR(1) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("albumId") REFERENCES "albumData"("albumId"),
    PRIMARY KEY ("userId", "albumId")
);
CREATE TABLE IF NOT EXISTS "playlistData" (
    "playlistId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "playlistName" VARCHAR(255) NOT NULL,
    "playlistDescription" VARCHAR(255) NULL,
    "hasImage" CHAR(1) NOT NULL,
    "playlistImageFileExt" VARCHAR(10) NULL,
    "playlistLikesCount" INTEGER NOT NULL,
    "playlistDislikesCount" INTEGER NOT NULL,
    "isPublic" CHAR(1) NOT NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1')),
    CHECK ("hasImage" IN ('0', '1')),
    CHECK ("isPublic" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "playlistLikeDislikeData" (
    "userId" INTEGER NOT NULL,
    "playlistId" INTEGER NOT NULL,
    "isLike" CHAR(1) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("playlistId") REFERENCES "playlistData"("playlistId"),
    PRIMARY KEY ("userId", "playlistId")
);
CREATE TABLE IF NOT EXISTS "playlistSongData" (
    "playlistId" INTEGER NOT NULL,
    "songId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("playlistId") REFERENCES "playlistData"("playlistId"),
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    PRIMARY KEY ("playlistId", "songId")
);
"""


def reinitializeDatabase():
    try:
        db_connection = sqlite3.connect("./db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.executescript(init_script)
        db_connection.commit()
        db_connection.close()

        print("[MESSAGE]: Database reinitialized successfully.")
    except Exception as e:
        f = open("logs/init_db.log", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        print("[ERROR]: Error in reinitializing database.")
    finally:
        return
