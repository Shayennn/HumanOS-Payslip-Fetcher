from datetime import datetime
import os
from pprint import pprint
import dotenv
import requests

APP_VERSION = "8.48"

session = requests.Session()
session.headers.update(
    {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "*/*",
        "LanguageID": "2",
        "Accept-Language": "en;q=1.0",
        "User-Agent": f"HumanOS/${APP_VERSION} (com.itcat.HumanOS; build:1; iOS 17.4.1) Alamofire/${APP_VERSION}",
        "DeviceOSType": "2",
        "AppVersion": APP_VERSION,
    }
)

def login(user, password, firebase_token=None):
    if firebase_token is None:
        firebase_token = ""
    data = {
        "AppVersion": APP_VERSION,
        "DeviceName": "iPhone12,5",
        "FirebaseToken": firebase_token,
        "Password": password,
        "TimeZone": "420",
        "UserName": user,
    }
    url = "https://api.humanos.biz/api/v35.0/Main/PreLogin"
    response = session.post(url, data=data)
    res_data = response.json()
    if not res_data["Success"]:
        raise Exception(res_data["Result"])
    session.headers.update(
        {
            "Accept": "*/*",
            "UserID": f"{res_data["Data"]["UserID"]}",
            "AppVersion": APP_VERSION,
            "ClientID": f"{res_data["Data"]["ClientID"]}",
            "Accept-Language": "en;q=1.0",
            "Token": f"{res_data["Data"]["Token"]}",
            "DeviceOSType": "2",
            "User-Agent": f"HumanOS/${APP_VERSION} (com.itcat.HumanOS; build:1; iOS 17.4.1) Alamofire/${APP_VERSION}",
            "PlatformType": "2",
            "TimeZone": "420",
            "LanguageID": "2",
        }
    )
    return res_data["Data"]

def get_payslips(year=None):
    if year is None:
        year = datetime.now().year
    url = f"https://api.humanos.biz/api/v35.0/PaySlip/GetPaySlipList"
    response = session.get(url, params={
        "onYear": year
    })
    res_data = response.json()
    if not res_data["Success"]:
        raise Exception(res_data["Result"])
    return res_data["Data"]

def get_payslip(installment_id):
    url = f"https://api.humanos.biz/api/v35.0/PaySlip/GetPaySlipDetail"
    response = session.get(url, params={
        "installmentID": installment_id
    })
    res_data = response.json()
    if not res_data["Success"]:
        raise Exception(res_data["Result"])
    return res_data["Data"]

def get_payslip_pdf(installment_id):
    url = f"https://api.humanos.biz/api/v35.0/PaySlip/DownloadPaySlip"
    response = session.get(url, params={
        "installmentID": installment_id
    })
    pdf = response.content
    pdf_name = response.headers["Content-Disposition"].split("filename=")[1].replace('/', "_").replace('\\', "_")
    return (pdf_name, pdf)

def logout():
    url = "https://api.humanos.biz/api/v35.0/Main/Logout"
    response = session.post(url)
    res_data = response.json()
    if not res_data["Success"]:
        raise Exception(res_data["Result"])
    return res_data["Result"]


if __name__ == "__main__":
    # load user password token from environment variable
    dotenv.load_dotenv()

    user = os.getenv("HUMANOS_USER")
    password = os.getenv("HUMANOS_PASSWORD")
    firebase_token = os.getenv("FIREBASE_TOKEN")

    data = login(user, password, firebase_token)
    print(f"Logged in as {data["MyContact"][0]["FName"]} {data["MyContact"][0]["LName"]} success")
    try:
        payslips = get_payslips()
        pprint(payslips)
        payslip = get_payslip(payslips['Data'][-1]["InstallmentID"])
        pprint(payslip)
        _, pdf = get_payslip_pdf(payslips['Data'][-1]["InstallmentID"])
        with open(f"Slip_{payslip['SlipDetail'][0]["PayDate"][:10]}.pdf", "wb") as f:
            f.write(pdf)
    except Exception as e:
        pprint(e)
    finally:
        pprint(logout())
