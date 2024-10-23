import cv2
import zxing

def decode_barcodes(frame):
    reader = zxing.BarCodeReader()
    print(reader.zxing_version, reader.zxing_version_info)
    barcode = reader.decode(frame, try_harder=True)
    result = str(barcode)
    print('BC Barcode info ' + result)
    return result

def decode_barcodes_pybar(frame):
    barcodes = pyzbar.decode(cv2.imread(frame))
    barcode_info = ''
    for barcode in barcodes:
        barcode_info = barcode_info + ' ' + barcode.data.decode('utf-8')
    return barcode_info
