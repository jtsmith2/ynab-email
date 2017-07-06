#!/usr/bin/python3.6

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pynYNAB.Client import nYnabClient
from pynYNAB.connection import nYnabConnection
from pynYNAB.schema.budget import Payee, Transaction

import datetime


def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addr_list)

    htmlmessage = '<html><head></head><body>'+message+'</body></html>'

    part1 = MIMEText(message, 'plain')
    part2 = MIMEText(htmlmessage, 'html')

    msg.attach(part1)
    msg.attach(part2)
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, msg.as_string())
    server.quit()
    return problems


def main():

    ynabUser = ''         # Example: someone@domain.com
    ynabPassword = ''
    ynabBudgetName = 'My Budget'            # Example:  My Budget

    print('Getting YNAB info')

    connection = nYnabConnection(ynabUser, ynabPassword)
    connection.init_session()
    client = nYnabClient(nynabconnection=connection, budgetname=ynabBudgetName)

    cats = {}
    subs = {}
    balances = {}

    #Creates hiarichy structure of category/subcategory and only those that have the keyword in YNAB subcategory notes section
    for cat in client.budget.be_master_categories:
            cats[cat.name]=cat
            subs[cat.name+'_subs'] = {}
            for subcat in client.budget.be_subcategories:
                    if subcat.entities_master_category_id == cat.id:
                            subs[cat.name+'_subs'][subcat.name] = subcat
        
    #Gets current month budget calculations
    for b in client.budget.be_monthly_subcategory_budget_calculations:
            if b.entities_monthly_subcategory_budget_id[4:11]==(datetime.datetime.now().strftime('%Y-%m')):
                    balances[b.entities_monthly_subcategory_budget_id[12:]]=b
                    #print(b.entities_monthly_subcategory_budget_id[12:]+': ' + str(b.balance))
        
    #Displays the balance for each subcategory in the subs dict
    bal_str = '<p>'
    for cat in cats:
        if 'Internal' not in cat:
            if len(subs[cat+'_subs'])>0:
                    bal_str += '<b>'+cat+'</b> <br>'
                    for scat in subs[cat+"_subs"]:
                            #print(cat + ' - ' + scat)
                            bal_str += '&nbsp;&nbsp;&nbsp;&nbsp;'+ scat + ': ' + str(balances[subs[cat+"_subs"][scat].id].balance) + '<br>'

    print('Sending Email')

    sendemail('example@example.com',['example@example.com'],'',
              'YNAB Balances', bal_str, 'username', 'password', 'smtp.gmail.com:587')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        quit()
