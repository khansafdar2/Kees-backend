import contextlib
import tempfile

import OpenSSL.crypto
import requests
from django.conf import settings


class GenerateSession(object):

    def withCertificate(self, credentials, currency, txn_ref_no, url, amount):
        @contextlib.contextmanager
        def pfx_to_pem(pfx_path, pfx_password):
            ''' Decrypts the .pfx file to be used with requests. '''
            with tempfile.NamedTemporaryFile(suffix='.pem') as t_pem:
                f_pem = open(t_pem.name, 'wb')
                pfx = open(pfx_path, 'rb').read()
                p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)
                f_pem.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
                f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
                ca = p12.get_ca_certificates()
                if ca is not None:
                    for cert in ca:
                        f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
                f_pem.close()
                yield t_pem.name

        with pfx_to_pem(credentials.certificatePath, credentials.password) as cert:

            header = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "Registration": {
                    "Currency": currency,
                    "ReturnPath": settings.HOST_URL + "/ubl_response",
                    "TransactionHint": "CPT:Y;VCC:Y;",
                    "OrderID": txn_ref_no,
                    "OrderName": txn_ref_no,
                    "OrderInfo": txn_ref_no,
                    "Channel": "Web",
                    "Amount": amount,
                    "Customer": credentials.customerData,
                }
            }

            print(cert)
            response = requests.post(url, json=payload, headers=header, cert=cert)
            print(response.json())
            return response

    def withOutCertificate(self, credentials, currency, txn_ref_no, url, amount):
        header = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "Registration": {
                "Currency": currency,
                "ReturnPath": settings.HOST_URL + "/ubl_response",
                "TransactionHint": "CPT:Y;VCC:Y;",
                "OrderID": txn_ref_no,
                "OrderName": txn_ref_no,
                "OrderInfo": txn_ref_no,
                "Channel": "Web",
                "Amount": amount,
                "Customer": credentials.credentials["Customer Data"],
                "UserName": credentials.credentials["Username"],
                "Password": credentials.credentials["Password"]
            }
        }
        print(payload)

        response = requests.post(url, json=payload, headers=header)
        return response
