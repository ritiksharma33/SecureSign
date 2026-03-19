import qrcode
import json

def generate_qr(data, output):

    qr = qrcode.make(json.dumps(data))

    qr.save(output)