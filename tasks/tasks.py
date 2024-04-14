from celery.schedules import crontab
from tasks.workers import celery

import sqlite3
from datetime import datetime

from middleware.mail.mailer import send_daily_reminder, send_monthly_report

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        20.0, 
        testCelery.s(), 
        name='Reminder every 10 seconds.'
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=19, day_of_month='*'),
        sendDailyReminderMail.s(),
        name = 'Daily reminder everyday @7PM via mail.'
    )

    sender.add_periodic_task(
        crontab(day_of_month=1, month_of_year='*'),
        sendMonthlyReport.s(),
        name = 'Monthly Engagement Report @1st of every month via mail.'
    )

@celery.task
def testCelery():
    print('20 s once SENDING REMINDER MAIL')
    return '[MESSAGE] Every 20 second trigger.'


@celery.task
def sendDailyReminderMail():
    db_connection = sqlite3.connect("../db/app_data.db")
    db_cursor = db_connection.cursor()

    today_date = str(datetime.now().date())

    db_cursor.execute("SELECT userEmail, userFullName from userData WHERE userId IN (SELECT userId from loginLogs WHERE loginDate < ?)" , (today_date,))
    users = db_cursor.fetchall()

    db_connection.close()

    for user in users:
        send_daily_reminder(user[0], user[1])

    return '[MESSAGE] Daily reminder email sent.'


@celery.task
def sendMonthlyReport():
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute("SELECT userId, userEmail, userFullName from userData WHERE userRoleId = 2")
        creators = db_cursor.fetchall()

        db_connection.close()

        for creator in creators:
            the_stats = {}

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            the_stats["noOfSongs"] = db_cursor.execute("SELECT COUNT(*) FROM songData WHERE createdBy = ?", creator[0]).fetchone()[0]
            the_stats["noOfAlbums"] = db_cursor.execute("SELECT COUNT(*) FROM albumData WHERE createdBy = ?", creator[0]).fetchone()[0]

            # Group by songName, songPlaysCount, likesCount

            res = db_cursor.execute("SELECT songName, songPlaysCount, likesCount FROM songData WHERE createdBy = ?", creator[0]).fetchall()

            the_stats["songStats"] = []

            for song in res:
                the_stats["songStats"].append({
                    "songName": song[0],
                    "songPlaysCount": song[1],
                    "likesCount": song[2]
                })

            db_connection.close()


            # Send mail to creator

            send_monthly_report(creator[1], the_stats)

        return '[MESSAGE] Monthly report mail sent.'

    except Exception as e:
        print(e)
        return '[MESSAGE] Monthly report mail failed.'
