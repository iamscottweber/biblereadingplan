from bible_plan_json import bible_plan
import datetime
from collections import OrderedDict
import yagmail
import credentials
import calendar
from random import randrange
import requests
import sys

my_date = datetime.datetime.today()
today_human_readable = my_date.strftime('%Y-%m-%d')
day_of_week_human_readable = calendar.day_name[my_date.weekday()]  #'Wednesday'


def parse_bible_data(current_week,current_day):
    for week in bible_plan:
        if week['Week'] == str(current_week):
            ordered_week = OrderedDict(week)
            this_weeks_readings = ordered_week
            for i, (key, value) in enumerate(ordered_week.items()):
                if i == current_day + 1:
                    print(f"Todays reading is {value}")
                    if not value[-1].isdigit():
                        first_chapter = '1'
                    else: 
                        first_chapter = value.split(" ")[-1].split("-")[0]
                    if value.split(" ")[0].isdigit():
                        book = ' '.join(value.split(" "))
                    else: book = value.split(" ")[0]
                    final_url = generate_url(book,first_chapter)
                    send_mail(to_email=[credentials.to_email,credentials.to_email_alt],
                              subject=f"Today's ({day_of_week_human_readable}) reading is {value}",
                              content=f'<span>Bible Reading Plan for {day_of_week_human_readable} - {today_human_readable} </span><br/><span>Click here to open plan {final_url}</span>')
                    return final_url


def generate_url(book,first_chapter):
    base_url = 'https://www.bible.com/bible/116/'
    if ' ' in book: 
        book = book.replace(" ","")
    final_url = base_url + str(book[:3]) + "." + first_chapter + '.NLT'
    return final_url

def send_mail(to_email,subject,content,attachment=False):
    with yagmail.SMTP(credentials.from_email, credentials.pw) as yag:
        try:
            if attachment:
                yag.send(to_email, subject, content, attachment)
            else:
                yag.send(to_email, subject, content)
            print(f'Sent email to {to_email} success')
        except Exception as e:
            print(f"Email Failed to Send to {to_email}")
            pass


def test():
    for i in range(52):
        current_week = i + 1 #randrange(0,52)
        for x in range(7):
            current_day = x # randrange(0,6)
            print(f"Testing current_week: {current_week} and current_day: {current_day} ")
            final_url = parse_bible_data(current_week,current_day)
            print(f"final_url: {final_url}")
            if final_url == None:
                sys.exit(1)
            web_response(final_url)


def web_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f'{url} site exists')
    else:
        print(f'{url}  does not exist')
        sys.exit(1)

if __name__ == '__main__':
    current_week = my_date.isocalendar().week
    current_day = int(my_date.strftime('%w')) #sunday is 0
    print(f"current_week: {current_week} and current_day: {current_day} ")
    final_url = parse_bible_data(current_week,current_day)



