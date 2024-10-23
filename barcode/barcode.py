#from docbarcodes.extract import process_document
import re
from verify.process_barcode import process
from verify.forensics import text_matches_name, text_matches_birthday, text_has_valid_birthday_and_expiry

def barcode_valid(verification):
#    barcodes_raw, barcodes_combined = process_document(verification.document_isolated.path)
    import zxing
    reader = zxing.BarCodeReader()
    barcode = str(reader.decode(verification.document_isolated.path))
    matches = re.findall("raw='([^']+)'", str(barcode))
    fmatch = re.findall("format='([\w+]+)'", str(barcode))
    if not 'PDF_417' in fmatch:
        return False
    match = ''
    for m in matches:
        print(m)
        if len(m) > len(match):
            match = m
    verification.barcode_data = match
    verification.barcode_data_processed = process(match)
    verification.save()
    if not match:
        return False
    return text_has_valid_birthday_and_expiry(verification.barcode_data_processed, '')
