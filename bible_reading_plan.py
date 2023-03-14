from bible_plan_json import bible_plan
import datetime
from collections import OrderedDict
import yagmail
import credentials
import calendar
from random import randrange
import requests
import sys
from datetime import datetime, timedelta
import pandas as pd    
import numpy as np
from email.mime.text import MIMEText



def parse_bible_data(current_week,current_day):
    for week in bible_plan:
        if week['Week'] == str(current_week):
            this_weeks_readings = OrderedDict(week)
            for i, (key, value) in enumerate(this_weeks_readings.items()):
                if i == current_day + 1:
                    reference = value
                    category = key.split(" ")[0]
                    print(f"Todays reading is {reference}")
                    if not value[-1].isdigit():
                        first_chapter = '1'
                    else: 
                        first_chapter = reference.split(" ")[-1].split("-")[0]
                    if reference.split(" ")[0].isdigit():
                        book = ' '.join(reference.split(" "))
                    else: book = reference.split(" ")[0]
                    final_url = generate_url(book,first_chapter)
                    return final_url,reference,category

def generate_email_content():
    """Send email with last 5 days of readings also"""
    my_date = datetime.today()
    current_week = my_date.isocalendar().week
    current_day = int(my_date.strftime('%w')) #sunday is 0
    final_url,reference,category = parse_bible_data(current_week,current_day)
    day_of_week_human_readable = calendar.day_name[my_date.weekday()]  #'Wednesday'
    today_human_readable = my_date.strftime('%Y-%m-%d')
    html_table = generate_html_date_frame(bible_plan,reference)

    content = f"""
            <span>Bible Reading Plan for {day_of_week_human_readable} - {today_human_readable}
            </span><span>{category} - {reference}</span>
            <span>Click here to open plan {final_url}</span>
            <hr/>
            {html_table}
            <hr/>
            <span>Previous Readings</span>
            """
    x = 1
    for i in range(7):
        my_date = datetime.today() - timedelta(days=x)
        print(f"my_date: {my_date}")
        #bug if sunday then week needs +1
        current_week = my_date.isocalendar().week
        current_day = int(my_date.strftime('%w')) #sunday is 0
        if current_day == 0:  
            current_week = current_week + 1
        print(f"current_week: {current_week} and current_day: {current_day} ")
        final_url,reference,category = parse_bible_data(current_week,current_day)
        day_of_week_human_readable = calendar.day_name[my_date.weekday()]  #'Wednesday'
        today_human_readable = my_date.strftime('%Y-%m-%d')
        content += f"""
                <hr/>
                <span>Previous Reading for {day_of_week_human_readable} - {today_human_readable}</span>
                <span>{category} - {reference}</span>
                <span>Click here to open plan {final_url}</span>
                """
        x += 1
    print(f"content: {content}")
    return content
    

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

def generate_html_date_frame(json_list,todays_reference):
    df = pd.DataFrame(json_list) 
    df.reset_index(drop=True, inplace=True)
    df.set_index('Week', inplace=True)
    df = df.style.apply(lambda x: ['font-weight: bold; background-color: yellow'
               if value == todays_reference else '' for value in x]
               )
    fixed_html = df.to_html().replace("\n", "")
    HEADER = """
    <style>
        table, th, td {
        border: 1px solid #000000;
        border-collapse: collapse;
        text-align: center;
        }
    </style>
    """
    # <head>{HEADER}</head>
    html = f"""<html>
    <body>
    {fixed_html}
    </body>
    </html>
    """
    with open('test.html', 'w') as f:
        f.write(HEADER)
        f.write(df.to_html(classes='df'))
    print(f"html.....")
    print(html)
    return html


def test():
    for i in range(52):
        current_week = i + 1 #randrange(0,52)
        for x in range(7):
            current_day = x # randrange(0,6)
            print(f"Testing current_week: {current_week} and current_day: {current_day} ")
            final_url,reference,category = parse_bible_data(current_week,current_day)
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
    my_date = datetime.today()
    current_week = my_date.isocalendar().week
    current_day = int(my_date.strftime('%w')) #sunday is 0
    final_url,reference,category = parse_bible_data(current_week,current_day)
    day_of_week_human_readable = calendar.day_name[my_date.weekday()]  #'Wednesday'
    today_human_readable = my_date.strftime('%Y-%m-%d')
    print(f"current_week: {current_week} and current_day: {current_day} ")
    # to = credentials.to_email
    to = [credentials.to_email,credentials.to_email_alt]
    send_mail(to_email=to,
            subject=f"Today's ({day_of_week_human_readable}) reading is {reference}",
            content=generate_email_content())


