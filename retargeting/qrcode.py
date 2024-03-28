def make_qr_code(file, data):
    import segno
    qrcode = segno.make(data)
    qrcode.save(file)
