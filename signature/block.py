from PIL import Image, ImageDraw, ImageFont

def build_signature(signature_img, name, date, time, qr_path):

    canvas = Image.new("RGBA",(600,250),(255,255,255,255))

    sig = Image.open(signature_img).resize((300,120))
    canvas.paste(sig,(150,10))

    draw = ImageDraw.Draw(canvas)

    font = ImageFont.load_default()

    draw.text((300,150),name,anchor="mm",font=font)
    draw.text((300,180),date,anchor="mm",font=font)
    draw.text((300,200),time,anchor="mm",font=font)

    qr = Image.open(qr_path).resize((80,80))
    canvas.paste(qr,(20,160))

    return canvas