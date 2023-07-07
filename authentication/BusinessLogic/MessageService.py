
import requests
import datetime
import urllib.parse
from authentication.models import MessageProvider, MessageLogs
import json
import xmltodict


# from sms.BusinessLogic.sendSMS import sendSMS
# from authentication.models import MessageProvider
# provider = MessageProvider.objects.get(id=6)
# sendSMS.send_message(provider, '03000342350', 'Test Message', provider, None)

class MessageServiceProvider(object):

    # Message Sending
    def send_message(self, phone, message, provider=None, provider_type=None, ip_address=None):
        try:
            message_service = MessageProvider.objects.filter(deleted=False).first()
            # if provider_type is None:
            #     provider_type = self.provider_type

            message = message.replace('#', '')
            phone = phone.replace(' ', '')

            if message_service:
                if message_service.provider_type == 'vodafone':
                    username = message_service.provider_username
                    password = message_service.provider_password
                    mask = message_service.provider_mask
                    source_id = message_service.provider_sid

                    api = "https://connectsms.vodafone.com.qa/SMSConnect/SendServlet?application={username}&password={password}&content={content}&destination={destination}&source={source_id}&mask={mask}".format(username=username,
                                                                                                                                                                                                                   password=password,
                                                                                                                                                                                                                   content=message,
                                                                                                                                                                                                                   destination=phone,
                                                                                                                                                                                                                   source_id=source_id,
                                                                                                                                                                                                                   mask=mask)
                    response = requests.get(api)
                elif provider_type == "Dot Klick":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://csms.dotklick.com/api_sms/api.php?key={key}&receiver={to}&sender={mask}&msgdata={message}".format(
                        key=provider.provider_username,
                        mask=provider.provider_mask,
                        to=phone,
                        message=urllib.parse.quote_plus(message))

                    response = requests.get(url)
                    if response.status_code == 200:
                        response_in_json = json.loads(response.text)
                        if response_in_json['response'] is not None:
                            if response_in_json['response']['description'] is not None:
                                message_response = response_in_json['response']['description']
                                MessageLogs.objects.create(message=message,
                                                           number=phone,
                                                           provider=provider.provider_type,
                                                           mask=provider.provider_mask,
                                                           created_at=datetime.datetime.now(),
                                                           updated_at=datetime.datetime.now(),
                                                           message_status=True,
                                                           message_response=message_response,
                                                           ip_address=ip_address)
                                return True, ""
                            else:
                                message_response = "SMS Server responded by " + str(response.status_code)
                                MessageLogs.objects.create(message=message,
                                                           number=phone,
                                                           provider=provider.provider_type,
                                                           mask=provider.provider_mask,
                                                           created_at=datetime.datetime.now(),
                                                           updated_at=datetime.datetime.now(),
                                                           message_status=False,
                                                           message_response=message_response,
                                                           ip_address=ip_address)
                                return False, message_response
                        else:
                            message_response = "SMS Server responded by " + str(response.status_code)
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=False,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return False, message_response
                    else:
                        message_response = "SMS Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "Telenor":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    # getting the session id
                    url = "https://telenorcsms.com.pk:27677/corporate_sms2/api/auth.jsp"
                    params = {"msisdn": provider.provider_msisdn, "password": provider.provider_password}
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        xml_data = xmltodict.parse(response.text)
                        if xml_data["corpsms"]["response"] == "OK":
                            session_id = xml_data["corpsms"]["data"]
                            # sending sms
                            url = "https://telenorcsms.com.pk:27677/corporate_sms2/api/sendsms.jsp"
                            params = {"session_id": session_id, "to": phone, "text": message,
                                      "mask": provider.provider_mask}
                            url_response = requests.get(url, params=params)
                            if url_response.status_code == 200:
                                xml_data = xmltodict.parse(url_response.text)
                                if xml_data["corpsms"]["response"] == "OK":
                                    message_response = xml_data["corpsms"]["response"]
                                    MessageLogs.objects.create(message=message,
                                                               number=phone,
                                                               provider=provider.provider_type,
                                                               mask=provider.provider_mask,
                                                               created_at=datetime.datetime.now(),
                                                               updated_at=datetime.datetime.now(),
                                                               message_status=True,
                                                               message_response=message_response,
                                                               ip_address=ip_address)
                                    return True, message_response
                            else:
                                message_response = "Server responded by " + str(response.status_code)
                                MessageLogs.objects.create(message=message,
                                                           number=phone,
                                                           provider=provider.provider_type,
                                                           mask=provider.provider_mask,
                                                           created_at=datetime.datetime.now(),
                                                           updated_at=datetime.datetime.now(),
                                                           message_status=False,
                                                           message_response=message_response,
                                                           ip_address=ip_address)
                                return False, message_response
                        else:
                            message_response = "Session Id not fetched"
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=False,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return False, message_response
                    else:
                        message_response = "Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "Mobilink":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]

                    url = "https://connect.jazzcmt.com/sendsms_url.html"

                    params = {
                        "Username": provider.provider_username,
                        "Password": provider.provider_password,
                        "From": provider.provider_mask,
                        "To": phone,
                        "Message": message
                    }
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        message_response = response.text
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "First Value":
                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    phone = phone.replace(" ", "")
                    ###### Number formating ######
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    header = {
                        "Host": "api.infobip.com"
                    }

                    url = "http://sms.myvaluefirst.com/smpp/sendsms?username={username}&password={password}&to={to}&from={mask}&text={message}".format(
                        username=provider.provider_username,
                        password=provider.provider_password,
                        mask=provider.provider_mask,
                        to=phone,
                        message=urllib.parse.quote_plus(message)
                    )
                    response = requests.get(url, headers=header)
                    if response.status_code == 200:
                        message_response = response.text
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == 'Out Reach':
                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://outreach.pk/api/sendsms.php/sendsms/url"

                    params = {
                        "id": provider.provider_username,
                        "pass": provider.provider_password,
                        "mask": provider.provider_mask,
                        "to": phone,
                        "msg": message,
                        "lang": provider.message_lang,
                        "type": provider.message_type
                    }
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        xml_data = xmltodict.parse(response.text)
                        print(xml_data)
                        if xml_data["corpsms"]["type"] == "Success":
                            message_response = xml_data["corpsms"]["response"]
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=True,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return True, ""
                        else:
                            message_response = "Server responded by " + str(response.status_code)
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=False,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return False, message_response
                    else:
                        message_response = "Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == 'Country SMS':
                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) > 8:
                        phone = "971" + phone[-9:]

                    url = "http://api.smscountry.com/SMSCwebservice_bulk.aspx"

                    params = {
                        "User": provider.provider_username,
                        "passwd": provider.provider_password,
                        "mobilenumber": phone,
                        "message": message,
                        "sid": provider.provider_sid,
                        "mtype": provider.message_type,
                        "DR": provider.message_dr
                    }
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        message_response = response.text
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_username,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "M4 SMS":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://api.m4sms.com/api/sendsms?id=" + provider.provider_username + "&pass=" + provider.provider_password + "&mobile=" + phone + "&brandname=" + provider.provider_mask + "&msg=" + urllib.parse.quote_plus(
                        message) + "&language=" + provider.message_lang

                    response = requests.get(url)
                    response_data = json.loads(response.text)
                    if response_data['Response'] == 'sent':
                        message_response = response_data['Response']
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(response_data['Response'])
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "Intellexal Solution SMS":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://bsms.its.com.pk/api.php?key=" + provider.provider_username + "&receiver=" + phone + "&sender=" + provider.provider_mask + "&msgdata=" + urllib.parse.quote_plus(
                        message) + "&response_type=json"

                    response = requests.get(url)
                    response_data = json.loads(response.text)
                    if response_data['response'] is not None:
                        if response_data['response']['status'] == 'Success':
                            message_response = response_data['response']['description']
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=True,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return True, ""
                        else:
                            message_response = "Server responded by " + str(response_data['response']['description'])
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=False,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return False, message_response
                    else:
                        message_response = "Server not responded"
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "BIZ SMS":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://api.bizsms.pk/api-send-branded-sms.aspx?username=" + provider.provider_username + "&pass=" + provider.provider_password + "&text=" + urllib.parse.quote_plus(
                        message) + "&masking=" + provider.provider_mask + "&destinationnum=" + phone + "&language=" + provider.message_lang

                    response = requests.get(url)
                    response_data = xmltodict.parse(response.text)
                    if response_data['html']['body']['form']['div']['b']['span']['#text'] == 'SMS Sent Successfully.':
                        message_response = response_data['html']['body']['form']['div']['b']['span']['#text']
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(
                            response_data['html']['body']['form']['div']['b']['span']['#text'])
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "PRO SMS":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "https://panel.prosms.pk/api/quick/message"

                    params = {
                        "user": provider.provider_username,
                        "password": provider.provider_password,
                        "mask": provider.provider_mask,
                        "to": phone,
                        "message": message
                    }
                    response = requests.get(url, params=params)
                    response_in_json = json.loads(response.text)
                    if response_in_json['status'] == 'OK':
                        message_response = response_in_json['msg']
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "Server responded by " + str(response_in_json['msg'])
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "SMS Bundle":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "https://portal.smsbundles.com/sendsms_url.html"
                    params = dict(Username=provider.provider_username, Password=provider.provider_password,
                                  From=provider.provider_mask, To=phone, Message=message)
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        message_response = response.text
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=True,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return True, ""
                    else:
                        message_response = "SMS Server responded by " + str(response.status_code)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response

                elif provider_type == "Zong":

                    if provider is None:
                        provider = MessageProvider.objects.get(id=self.id)

                    ###### Number formating ######
                    phone = phone.replace(" ", "")
                    if len(phone) == 11 and phone[:1] == "0":
                        phone = "92" + phone[1:]
                    elif phone[:1] == "+" and len(phone) == 13:
                        phone = phone[1:]
                    elif len(phone) == 14 and phone[:4] == "0092":
                        phone = phone[2:]
                    elif len(phone) == 14 and phone[:4] == "0+92":
                        phone = phone[2:]
                    elif len(phone) == 10 and phone[:1] == "3":
                        phone = "92" + phone

                    url = "http://cbs.zong.com.pk/reachrestapi/home/SendQuickSMS"
                    body_data = {
                        "loginId": provider.provider_username,
                        "loginPassword": provider.provider_password,
                        "Destination": phone,
                        "Mask": provider.provider_mask,
                        "Message": message,
                        "UniCode": "0",
                        "ShortCodePrefered": "n"
                    }
                    response = requests.post(url, data=body_data, verify=False)
                    sms_response = response.text.split('|')
                    if response.status_code == 200:
                        if sms_response is not None:
                            if sms_response[1] == 'success':
                                message_response = response.text
                                MessageLogs.objects.create(message=message,
                                                           number=phone,
                                                           provider=provider.provider_type,
                                                           mask=provider.provider_mask,
                                                           created_at=datetime.datetime.now(),
                                                           updated_at=datetime.datetime.now(),
                                                           message_status=True,
                                                           message_response=message_response,
                                                           ip_address=ip_address)
                                return True, ""
                            else:
                                message_response = "SMS Server responded by " + str(response.text)
                                MessageLogs.objects.create(message=message,
                                                           number=phone,
                                                           provider=provider.provider_type,
                                                           mask=provider.provider_mask,
                                                           created_at=datetime.datetime.now(),
                                                           updated_at=datetime.datetime.now(),
                                                           message_status=False,
                                                           message_response=message_response,
                                                           ip_address=ip_address)
                                return False, message_response
                        else:
                            message_response = "SMS Server responded by " + str(response.text)
                            MessageLogs.objects.create(message=message,
                                                       number=phone,
                                                       provider=provider.provider_type,
                                                       mask=provider.provider_mask,
                                                       created_at=datetime.datetime.now(),
                                                       updated_at=datetime.datetime.now(),
                                                       message_status=False,
                                                       message_response=message_response,
                                                       ip_address=ip_address)
                            return False, message_response
                    else:
                        message_response = "SMS Server responded by " + str(response.text)
                        MessageLogs.objects.create(message=message,
                                                   number=phone,
                                                   provider=provider.provider_type,
                                                   mask=provider.provider_mask,
                                                   created_at=datetime.datetime.now(),
                                                   updated_at=datetime.datetime.now(),
                                                   message_status=False,
                                                   message_response=message_response,
                                                   ip_address=ip_address)
                        return False, message_response
        except Exception as e:
            log = "Exception " + str(e)
            return False, log
