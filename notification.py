import serial
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


sender_email = "tanabetest1230@gmail.com"
receiver_email = "yukiko202201@gmail.com"
password = "cvztowvbvyirjbwp"  


serial_port = 'COM5'  
baud_rate = 9600

def send_email():
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "6cm以内の通知"

    
    body = "窓に注意！"
    message.attach(MIMEText(body, "plain"))

    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("メールが送信されました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        server.quit()
def extract_distance(data):
    match = re.search(r'(\d+)\s*cm', data)
    if match:
        return int(match.group(1))
    return None
try:
    ser = serial.Serial(serial_port, baud_rate)
    print(f"{serial_port}に接続しました")
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            print("Received data:", data)
            distance = extract_distance(data)
            if distance is not None and 0 <= distance <= 6:
                send_email()
except serial.SerialException as e:
    print(f"シリアルポートのエラー: {e}")
except Exception as e:
    print(f"予期しないエラーが発生しました: {e}")
finally:
    if ser.is_open:
        ser.close()
