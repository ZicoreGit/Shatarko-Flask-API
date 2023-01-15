from flask import Flask, request, jsonify
import pymysql
from email.message import EmailMessage
import smtplib
import ssl
import random
import requests
import json

# email credential
email_sender = 'zicoretechasif@gmail.com'

email_password = 'ojjtgtewksjpwgvo'

# mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
#                        cursorclass=pymysql.cursors.DictCursor)
# # mycursor = mydb.cursor(buffered=True)
# # cursorclass=pymysql.cursors.DictCursor
# mycursor = mydb.cursor()


app = Flask(__name__)


@app.route("/")
def home():
    return "<p>Shatarko API</p>"


# user registration form route
@app.route('/registration', methods=['POST'])
def registration():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()

    username = request.form.get('user_name')
    userphonenumber = request.form.get('user_phonenumber')
    userpassword = request.form.get('user_password')
    useremail = request.form.get('user_email')
    usergender = request.form.get('user_gender')
    userprofilepic = request.form.get('user_profilepic')
    userdateofbirth = request.form.get('user_dateofbirth')
    userbloodgroup = request.form.get('user_bloodgroup')
    useraddress = request.form.get('user_address')
    useracoountcreationtime = request.form.get('user_accountcreationtime')
    userfirebasemessagingtoken = request.form.get('firebase_messagingtoken')

    findusersql = 'SELECT user_id FROM appusers WHERE user_phone_number = %s'
    finduserval = (userphonenumber,)
    mycursor.execute(findusersql, finduserval)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        print('user already exits')
        return jsonify([{'status': str('0')}])
    else:
        sql = 'INSERT INTO appusers (user_name,user_phone_number,user_password,user_email,user_gender,' \
              'user_profile_pic,user_date_of_birth,user_blood_group,user_address,user_account_creation_time,' \
              'user_firebase_messaging_token) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        val = (
            username, userphonenumber, userpassword, useremail, usergender, userprofilepic, userdateofbirth,
            userbloodgroup,
            useraddress, useracoountcreationtime, userfirebasemessagingtoken,)
        mycursor.execute(sql, val)
        mydb.commit()
        print('Registration successfully.')
        return jsonify([{'status': str('1')}])


#
# # user log in route
@app.route('/login', methods=['POST'])
def login():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()

    userphonenumber = request.form.get('user_phonenumber')
    firebasemessagingtoken = request.form.get('firebase_messaging_token')
    # matching firebase messaging token
    matchingtokensql = 'SELECT user_firebase_messaging_token FROM appusers WHERE user_phone_number = %s'
    matchingtokenval = (userphonenumber,)
    mycursor.execute(matchingtokensql, matchingtokenval)
    mydb.commit()
    result = mycursor.fetchall()
    print(type(result))
    if result:
        if str(result[0]['user_firebase_messaging_token']) == firebasemessagingtoken:
            sql = "SELECT user_id,user_name,user_phone_number,user_password from appusers WHERE user_phone_number = %s"
            val = (userphonenumber,)
            mycursor.execute(sql, val)
            mydb.commit()
            result = mycursor.fetchall()
            if result:
                return jsonify(result)
            else:
                return jsonify([{'user_password': str('0')}])
        else:
            # first update firebase messaging token
            updatetokensql = 'UPDATE appusers SET user_firebase_messaging_token = %s WHERE user_phone_number = %s '
            updatetokenval = (firebasemessagingtoken, userphonenumber)
            mycursor.execute(updatetokensql, updatetokenval)
            mydb.commit()
            # user profile data
            sql = "SELECT user_id,user_name,user_phone_number,user_password from appusers WHERE user_phone_number = %s"
            val = (userphonenumber,)
            mycursor.execute(sql, val)
            mydb.commit()
            result = mycursor.fetchall()
            if result:
                return jsonify(result)
            else:
                return jsonify([{'user_password': str('0')}])
    else:
        return jsonify([{'user_password': str('0')}])


@app.route('/otpSystem', methods=['POST'])
def otpSystem():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()

    # make a random number for otp
    otpCode = str(random.randint(1000, 2000))
    print(otpCode)

    email_receiver = request.form.get('email')
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': email_receiver})
    status = response.json()['status']
    if status == "valid":
        print('Email valid')
        subject = 'Shatarko OTP'

        body = 'Shatarko otp is:' + otpCode

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, em.as_string())
            return jsonify({'status': str(otpCode)})

    elif status == "invalid":
        print('Email invalid')
        return jsonify({'status': str('Email invalid')})

    else:
        print('Email is unknown.')
        return jsonify({'status': str('Email is unknown')})


@app.route('/searchDevice', methods=['POST'])
def searchDevice():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    devicecode = request.form.get('device_code')

    sql = "SELECT device_flag from availabledevices WHERE device_code = %s"
    val = (devicecode,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        for row in result:
            if row[0] == '0':
                print("Found the hub")
                return jsonify({'device_status': str('1')})
            else:
                print("It is not your device.")
                return jsonify({'device_status': str('2')})
    else:
        print("No hub found.")
        return jsonify({'device_status': str('0.')})


@app.route('/addDevice', methods=['POST'])
def addDevice():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    global x, y
    devicename = request.form.get('device_name')
    devicecode = request.form.get('device_code')
    username = request.form.get('user_name')

    sql = "SELECT device_id from availabledevices WHERE device_code = %s"
    val = (devicecode,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        for row in result:
            y = row[0]
            print(y)
            sql2 = "SELECT user_id from users WHERE user_name = %s"
            val2 = (username,)
            mycursor.execute(sql2, val2)
            mydb.commit()
            result2 = mycursor.fetchall()
            if result:
                for row2 in result2:
                    x = row2[0]
                    print(x)
                    sql3 = "Insert into owningdevices (device_id,user_id,device_name) values (%s,%s,%s)"
                    val3 = (int(y), int(x), devicename,)
                    mycursor.execute(sql3, val3)
                    mydb.commit()
                    sql4 = "UPDATE availabledevices SET device_flag = %s WHERE device_id = %s"
                    val4 = (str(1), int(y))
                    mycursor.execute(sql4, val4)
                    mydb.commit()
                    print("Device registered")
                    return jsonify({'device_status': str('1')})
    else:
        print("Something went wrong")
        return jsonify({'device_status': str('0')})


@app.route('/searchContact', methods=['POST'])
def searchContact():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    userid = request.form.get('user_id')
    contactphonenumber = request.form.get('contact_phonenumber')

    # check he or she already addded or not as a friend or julonto friend
    sql = "SELECT status_flag FROM emergency_contact INNER JOIN appusers ON appusers.user_id = emergency_contact.receiver_id  WHERE appusers.user_phone_number= %s AND emergency_contact.sender_id = %s"
    val = (contactphonenumber, userid,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        return result
    else:
        findsql = "SELECT user_id, user_name, user_phone_number,user_gender from appusers WHERE user_phone_number = %s"
        findval = (contactphonenumber,)
        mycursor.execute(findsql, findval)
        mydb.commit()
        result = mycursor.fetchall()
        if result:
            return result
        else:
            return jsonify([{'status': str('0')}])


@app.route('/sentRequest', methods=['POST'])
def sentRequest():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    senderid = request.form.get('sender_id')
    receiverid = request.form.get('receiver_id')
    relationshipstatus = request.form.get('relationship_status')
    sendingTime = request.form.get('sending_time')

    sql = "Insert into emergency_contact (sender_id,receiver_id,relationship_status,status_flag,sending_time,receiving_time,recjecting_time,blocking_time) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (int(senderid), int(receiverid), relationshipstatus, 1, sendingTime, 0, 0, 0,)
    mycursor.execute(sql, val)
    mydb.commit()
    usernamesql = "SELECT user_name FROM appusers WHERE user_id = %s"
    usernameval = (int(senderid),)
    mycursor.execute(usernamesql, usernameval, )
    mydb.commit()
    name = mycursor.fetchall()
    print(name[0]['user_name'])

    firebasetokensql = "SELECT user_firebase_messaging_token FROM appusers WHERE user_id = %s"
    firebasetokenval = (int(receiverid),)
    mycursor.execute(firebasetokensql, firebasetokenval, )
    mydb.commit()
    result = mycursor.fetchall()
    print(result[0]['user_firebase_messaging_token'])
    # # firebase
    serverToken = 'AAAA5aRwcnw:APA91bHnj1yMYLHLOBX5fXfBioS2OF8Acvrjb8b-2ha_XMPHTlYf6NgzAaGAZHDQgefeHUS_j0EM_lsXsWpEZMiVJFtEprln3SsqeEVRlbU2cCDNDMN-PnrZvdaa_0hYb_UqOdonVDRP'
    deviceToken = result[0]['user_firebase_messaging_token']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }
    # end
    body = {
        'notification': {
            'title': 'Shatarko',
            'body': name[0]['user_name'] + ' send you a request ',
            "android_channel_id": "shatarko-1002"
        },
        'data': {
            'name': 'request',
        },
        'to':
            deviceToken,
        'priority': 'high',

    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    print(response.status_code)

    print(response.json())
    print('Request Sent Successfully')
    return jsonify([{'status': str('1')}])


@app.route('/showContact', methods=['POST'])
def showContact():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    userid = request.form.get('user_id')
    sql = "SELECT id,emergency_contact.status_flag,appusers.user_name,appusers.user_phone_number, emergency_contact.relationship_status from emergency_contact INNER JOIN appusers ON appusers.user_id = emergency_contact.receiver_id WHERE sender_id = %s AND (status_flag = 1 OR status_flag = 0)"
    val = (userid,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        return result
    else:
        return jsonify([{'status': str('0')}])


@app.route('/showRequest', methods=['POST'])
def showRequest():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    userid = request.form.get('user_id')
    sql = "SELECT id,appusers.user_id,appusers.user_name,appusers.user_phone_number, emergency_contact.relationship_status from emergency_contact INNER JOIN appusers ON appusers.user_id = emergency_contact.sender_id WHERE receiver_id = %s AND status_flag = 1"
    val = (userid,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        return result
    else:
        return jsonify([{'status': str('0')}])


@app.route('/measEmergencycontact', methods=['POST'])
def measEmergencycontact():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    userid = request.form.get('user_id')
    sql = "SELECT id,appusers.user_id,appusers.user_name,appusers.user_phone_number, emergency_contact.relationship_status from emergency_contact INNER JOIN appusers ON appusers.user_id = emergency_contact.sender_id WHERE receiver_id = %s AND status_flag = 0"
    val = (userid,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    if result:
        return result
    else:
        return jsonify([{'status': str('0')}])


@app.route('/acceptRequest', methods=['POST'])
def acceptRequest():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    contactid = request.form.get('contact_id')
    userid = request.form.get('user_id')
    username = request.form.get('user_name')
    sql = "UPDATE emergency_contact SET status_flag = %s WHERE emergency_contact.id = %s"
    val = (str(0), contactid)
    mycursor.execute(sql, val)
    mydb.commit()
    firebasetokensql = " SELECT user_firebase_messaging_token FROM appusers WHERE user_id = %s"
    firebasetokenval = (int(userid),)
    mycursor.execute(firebasetokensql, firebasetokenval, )
    mydb.commit()
    result = mycursor.fetchall()
    print(result[0]['user_firebase_messaging_token'])
    # # firebase
    serverToken = 'AAAA5aRwcnw:APA91bHnj1yMYLHLOBX5fXfBioS2OF8Acvrjb8b-2ha_XMPHTlYf6NgzAaGAZHDQgefeHUS_j0EM_lsXsWpEZMiVJFtEprln3SsqeEVRlbU2cCDNDMN-PnrZvdaa_0hYb_UqOdonVDRP'
    deviceToken = result[0]['user_firebase_messaging_token']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }
    # end
    body = {
        'notification': {
            'title': 'Shatarko',
            'body': username + ' accept your request ',
            "android_channel_id": "shatarko-1002"
        },
        'data': {
            'name': 'request',
        },
        'to':
            deviceToken,
        'priority': 'high',

    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    print(response.status_code)

    print(response.json())
    print('Request Sent Successfully')

    return jsonify([{'status': str('1')}])


@app.route('/cancelRequest', methods=['POST'])
def cancelRequest():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    contactid = request.form.get('contact_id')
    sql = "DELETE FROM usercontacts WHERE contact_id = %s"
    val = (contactid,)
    mycursor.execute(sql, val)
    mydb.commit()
    return jsonify([{'status': str('1')}])


@app.route('/deleteContact', methods=['POST'])
def deleteContact():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    mycursor = mydb.cursor()
    contactid = request.form.get('contact_id')
    print(contactid)
    sql = "DELETE FROM emergency_contact WHERE emergency_contact.id = %s"
    val = (contactid,)
    mycursor.execute(sql, val)
    mydb.commit()
    return jsonify([{'status': str('1')}])


@app.route('/sendingPanic', methods=['POST'])
def sendingPanic():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    # mycursor = mydb.cursor(buffered=True)
    # cursorclass=pymysql.cursors.DictCursor
    mycursor = mydb.cursor()
    userid = request.form.get('user_id')
    username = request.form.get('user_name')
    panictype = request.form.get('panic_type')
    buttonpressedDate = request.form.get('button_pressed_date')
    buttonpressedtime = request.form.get('button_pressed_time')
    print(userid)
    print(panictype)
    stroringnotificationDataSql = 'INSERT INTO appuser_notification (user_id,panic_type,button_pressed_date,button_pressed_time) values (%s,%s,%s,%s)'
    stroringnotificationDataVal = (int(userid), panictype, buttonpressedDate, buttonpressedtime,)
    mycursor.execute(stroringnotificationDataSql, stroringnotificationDataVal)
    mydb.commit()
    sql = "SELECT appusers.user_name,appusers.user_firebase_messaging_token from emergency_contact INNER JOIN appusers ON appusers.user_id = emergency_contact.receiver_id WHERE sender_id = %s AND status_flag = 0"
    val = (userid,)
    mycursor.execute(sql, val)
    mydb.commit()
    result = mycursor.fetchall()
    for x in result:
        print(x['user_name'])
        print(x['user_firebase_messaging_token'])
        # firebase
        serverToken = 'AAAA5aRwcnw:APA91bHnj1yMYLHLOBX5fXfBioS2OF8Acvrjb8b-2ha_XMPHTlYf6NgzAaGAZHDQgefeHUS_j0EM_lsXsWpEZMiVJFtEprln3SsqeEVRlbU2cCDNDMN-PnrZvdaa_0hYb_UqOdonVDRP'
        deviceToken = x['user_firebase_messaging_token']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }
        # end
        body = {
            'notification': {
                'title': 'Shatarko',
                'body': username + ' pressed ' + panictype + ' button ',
                "android_channel_id": "shatarko-1001"
            },
            'to':
                deviceToken,
            'priority': 'high',

        }
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        print(response.status_code)

        print(response.json())
    return str(0)


# @app.route('/showNotification', methods=['POST'])
# def showNotification():
#     mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
#                            cursorclass=pymysql.cursors.DictCursor)
#     # mycursor = mydb.cursor(buffered=True)
#     # cursorclass=pymysql.cursors.DictCursor
#     mycursor = mydb.cursor()
#     userid = request.form.get('user_id')
#     collectnotificationsql = 'SELECT panic_type ,button_pressed_date,button_pressed_time FROM appuser_notification  WHERE appuser_notification.user_id = %s ORDER BY notification_id DESC'
#     collectnotificationval = (userid,)
#     mycursor.execute(collectnotificationsql, collectnotificationval, )
#     mydb.commit()
#     result = mycursor.fetchall()
#     if result:
#         return result
#     else:
#         return jsonify([{'status': str('0')}])


@app.route('/showNotification', methods=['POST'])
def showNotification():
    mydb = pymysql.connect(host='180.92.224.170', port=3307, user="root", passwd="", database="shatarko",
                           cursorclass=pymysql.cursors.DictCursor)
    mycursor = mydb.cursor()
    #contact ids
    conatctID = []
    senderid = request.form.get('user_id')
    conatctID.append(int(senderid))

    contactsql = "SELECT receiver_id from emergency_contact WHERE sender_id = %s AND status_flag = 0 "
    contactval = (senderid,)
    mycursor.execute(contactsql, contactval,)
    mydb.commit()
    result = mycursor.fetchall()
    for x in result:
        print(type(x['receiver_id']))
        conatctID.append(x['receiver_id'])

    # def Convert(string):
    #     li = list(string.split(','))
    #     return li
    #
    # print(conatctID)
    # party_ids = Convert(senderid)
    # # print(s)
    # # party_ids = [4, 7]
    in_params = ','.join(['%s'] * len(conatctID))
    sql = "SELECT appusers.user_name,appuser_notification.panic_type ,appuser_notification.button_pressed_date,appuser_notification.button_pressed_time FROM appuser_notification INNER JOIN appusers ON appuser_notification.user_id = appusers.user_id WHERE appuser_notification.user_id IN (%s) ORDER BY notification_id DESC" % in_params
    # val = (s,)
    mycursor.execute(sql, conatctID)
    mydb.commit()
    result = mycursor.fetchall()
    return result


if __name__ == '__main__':
    app.run(debug=True, host='192.168.10.144', port=800)
