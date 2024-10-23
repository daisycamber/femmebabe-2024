from docbarcodes.extract import process_document
import re
from verify.process_barcode import process
from verify.forensics import text_matches_name, text_matches_birthday

from PIL import Image as PIL
from pdf417decoder import PDF417Decoder


def barcode_valid(verification):
    image = PIL.open(verification.document.path)
    decoder = PDF417Decoder(image)
    barcodes_raw = ''
    if (decoder.decode() > 0):
        barcodes_raw = decoder.barcode_data_index_to_string(0)
#    barcodes_raw, barcodes_combined = process_document(verification.document.path)
    print(verification.document.path)
    print(barcodes_raw)
    matches = re.findall("raw='([^']+)'", str(barcodes_raw))
    fmatch = re.findall("format='([\w+]+)'", str(barcodes_raw))
    if not 'PDF_417' in fmatch:
        print(fmatch)
        print('Barcode format mismatch')
        return False
    match = ''
    for m in matches:
        print(m)
        if len(m) > len(match):
            match = m
    print(match)
    verification.barcode_data = match
    verification.barcode_data_processed = process(match)
    verification.save()
    if not match:
        return False
    processed = verification.barcode_data_processed
    verification = verification.user.verifications.last()
    if not text_matches_name(processed, verification.full_name) or not text_matches_birthday(processed, verification.birthday.strftime('%m/%d/%Y').replace('/', '')):
        return False
    if not verification.document_number or len(verification.document_number) < 8 or not verification.document_number in processed:
        print('Number not found on document')
        return False
    return True
