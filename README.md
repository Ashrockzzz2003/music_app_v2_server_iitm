# Music App v2 [IIT Madras]

## Tech Stack

| Purpose | Technology |
| --- | --- |
| Frontend | VueJS, HTML, CSS |
| Backend | Python, flask, redis, celery |
| Database | SQLite3 |

## How to run the app

> Pre-requisite: python, Node.js, redis

```bash
# Start Redis server

redis-server
```

## Backend

```bash
# From the root directory of the project
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Open a new terminal window at the root directory of the project
cd server
source venv/bin/activate
celery -A app.celery worker -l info # Worker for Celery

# Open a new terminal window at the root directory of the project
cd server
source venv/bin/activate
celery -A app.celery beat --max-interval 1 -l info # Beat for Celery

```

## Frontend

```bash
# From the root directory of the project
cd music_app_v2
npm i
npm run dev
```

## API Endpoints

- [x] Authentication
    - [x] Login RBAC
    - [x] Register (OTP-based)
    - [x] Forgot Password (OTP-based)
- [x] Admin
    - [x] Get Profile
    - [x] Language
        - [x] Create New Language
        - [x] Get All Languages
        - [x] Get Language by ID
        - [x] Update Language by ID
        - [x] Toggle Language Status by ID
    - [x] Genre
        - [x] Create New Genre
        - [x] Get All Genres
        - [x] Get Genre by ID
        - [x] Update Genre by ID
        - [x] Toggle Genre Status by ID
    - [x] Song
        - [x] Create New Song
        - [x] Query All Songs
        - [x] Get Song by ID
        - [x] Update Song by ID
        - [x] Delete Song by ID
        - [x] Toggle Song Status by ID
        - [x] Like/Dislike Song by ID
    - [x] Playlist
        - [x] Create New Playlist
        - [x] Query All Playlists (All Public Playlists)
        - [x] Get Playlist by ID
        - [x] Update Playlist by ID
        - [x] Delete Playlist by ID
        - [x] Add Song to Playlist
        - [x] Remove Song from Playlist
        - [x] Toggle Playlist Status (Public/Private) by ID
        - [x] Like/Dislike Playlist by ID
    - [x] Album
        - [x] Create New Album
        - [x] Query All Albums
        - [x] Get Album by ID
        - [x] Update Album by ID
        - [x] Delete Album by ID
        - [x] Add Song to Album
        - [x] Remove Song from Album
        - [x] Toggle Album Status by ID
    - [ ] Artist
        - [ ] Query All Artists
        - [ ] Get Artist by ID
        - [ ] Toggle Artist Status by ID
        - [ ] Query All Songs by Artist
        - [ ] Query All Albums by Artist
    - [ ] Stats
- [x] Public
    - [x] Language
        - [x] Get All Languages
        - [x] Get Language by ID
    - [x] Genre
        - [x] Get All Genres
        - [x] Get Genre by ID
    - [x] Song
        - [x] Query All Songs
        - [x] Get Song by ID
    - [x] Album
        - [x] Query All Albums
        - [x] Get Album by ID
    - [x] Playlist
        - [x] Query All Playlists (All Public Playlists)
        - [x] Get Playlist by ID
- [ ] User
    - [x] Register as Creator
    - [x] Get Profile
    - [x] Playlist
        - [x] Create New Playlist
        - [x] Query All Playlists (All Playlists that are visible)
        - [x] Get Playlist by ID
        - [x] Update Playlist by ID
        - [x] Delete Playlist by ID
        - [x] Add Song to Playlist
        - [x] Remove Song from Playlist
        - [x] Toggle Playlist Status (Public/Private) by ID
        - [x] Like/Dislike Playlist by ID
    - [x] Album
        - [x] All Albums
        - [x] Query All Albums
        - [x] Get Album by ID
    - [ ] Song
        - [x] Query All Songs
        - [x] Get Song by ID
        - [x] Like/Dislike Song by ID
- [x] Creator
    - [x] Get Profile
    - [x] Language
        - [x] Create New Language
        - [x] Get All Languages
        - [x] Get Language by ID
        - [x] Update Language by ID
        - [x] Toggle Language Status by ID
    - [x] Genre
        - [x] Create New Genre
        - [x] Get All Genres
        - [x] Get Genre by ID
        - [x] Update Genre by ID
        - [x] Toggle Genre Status by ID
    - [x] Song
        - [x] Create New Song
        - [x] Query All Songs
        - [x] My Songs (All Songs of User)
        - [x] Get Song by ID
        - [x] Update Song by ID
        - [x] Delete Song by ID
        - [x] Toggle Song Status by ID
        - [x] Like/Dislike Song by ID
    - [x] Playlist
        - [x] Create New Playlist
        - [x] Query All Playlists (All Visible Playlists)
        - [x] Get Playlist by ID
        - [x] Update Playlist by ID
        - [x] Delete Playlist by ID
        - [x] Add Song to Playlist
        - [x] Remove Song from Playlist
        - [x] Like/Dislike Playlist by ID
        - [x] Toggle Playlist Status (Public/Private) by ID
    - [x] Album
        - [x] Create New Album
        - [x] Query All Albums
        - [x] Get Album by ID
        - [x] Update Album by ID
        - [x] Delete Album by ID
        - [x] Add Song to Album
        - [x] Remove Song from Album
        - [x] Toggle Album Status by ID


`Ashwin Narayanan S`