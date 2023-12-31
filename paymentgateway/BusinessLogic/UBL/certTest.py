import contextlib
import OpenSSL.crypto
import os
import requests
import ssl
import tempfile


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


# HOW TO USE:
with pfx_to_pem('./Certificates/ALMIRAH_2020.pfx', 'ALMIRAH@2019') as cert:
    data = {
        "Registration": {
            "Currency": "PKR",
            "ReturnPath": "https://partner.ctdev.comtrust.ae/banktestnbad/Authorization.aspx?capture=true",
            "TransactionHint": "CPT:Y;VCC:Y;",
            "OrderID": "7210055701315195",
            "OrderName": "Paybill",
            "OrderInfo": "7210055701315195",
            "Channel": "Web",
            "Amount": "2000.00",
            "Customer": "ALMIRAH",
        }
    }
    url = "https://ipg.comtrust.ae:2443"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print(cert)
    response = requests.post(url, json=data, headers=header, cert=cert)
    print(response.json())
