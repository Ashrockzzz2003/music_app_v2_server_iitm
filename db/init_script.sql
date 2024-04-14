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

INSERT INTO "userRole" ("roleName") VALUES ('ADMIN');
INSERT INTO "userRole" ("roleName") VALUES ('CREATOR');
INSERT INTO "userRole" ("roleName") VALUES ('USER');

CREATE TABLE IF NOT EXISTS "userRegister" (
    "registrationId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userFullName" VARCHAR(255) NOT NULL,
    "userEmail" VARCHAR(255) NOT NULL UNIQUE,
    "userPassword" VARCHAR(255) NOT NULL,
    "userDob" VARCHAR(255) NOT NULL,
    "userGender" CHAR(1) NOT NULL,
    "userRoleId" INTEGER NOT NULL,
    "userOtp" VARCHAR(6) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userRoleId") REFERENCES "userRole"("roleId"),
    CHECK ("userGender" IN ('M', 'F', 'O'))
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
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userRoleId") REFERENCES "userRole"("roleId"),
    CHECK ("userGender" IN ('M', 'F', 'O')),
    CHECK ("userAccountStatus" IN ('0', '1', '2'))
);

CREATE TABLE IF NOT EXISTS "loginLogs"(
    "userId" INTEGER NOT NULL,
    "loginDate" TEXT NOT NULL,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId")
);

CREATE TABLE IF NOT EXISTS "forgotPasswordOtp"(
    "userId" INTEGER NOT NULL,
    "userOtp" VARCHAR(6) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("userId", "userOtp"),
    FOREIGN KEY ("userId") REFERENCES "userData"("userId")
);

INSERT INTO "userData" ("userFullName", "userEmail", "userPassword", "userDob", "userGender", "userAccountStatus", "userRoleId") 
VALUES ("Ashwin Narayanan S", 'admin@music.io', "password", '2003-10-13', "M", "1", 1);

INSERT INTO "userData" ("userFullName", "userEmail", "userPassword", "userDob", "userGender", "userAccountStatus", "userRoleId") 
VALUES ("Vaisakhkrishnan K", 'k_vaisakh@music.io', "password", '2001-10-13', "M", "1", 3);

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
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
);
CREATE TABLE IF NOT EXISTS "languageData" (
    "languageId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "languageCode" VARCHAR(255) NOT NULL,
    "languageName" VARCHAR(255) NULL,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
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
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    "likesCount" INTEGER NOT NULL DEFAULT 0,
    "dislikesCount" INTEGER NOT NULL DEFAULT 0,
    "songPlaysCount" INTEGER NOT NULL DEFAULT 0,
    "isActive" CHAR(1) NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NOT NULL,
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("songGenreId") REFERENCES "genreData"("genreId"),
    FOREIGN KEY ("songLanguageId") REFERENCES "languageData"("languageId"),
    FOREIGN KEY ("songAlbumId") REFERENCES "albumData"("albumId"),
    FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
    CHECK ("isActive" IN ('0', '1'))
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
    "noOfPlays" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "userData"("userId"),
    FOREIGN KEY ("songId") REFERENCES "songData"("songId"),
    PRIMARY KEY ("userId", "songId")
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
    "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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