def barcode_valid(verification):
    import re, os
    from django.conf import settings
    from .process_barcode import process
    from .forensics import text_matches_name, text_matches_birthday, text_has_valid_birthday_and_expiry
    from barcode.idscan import scan_id
    from .idscan import decode_barcode
#    if not scan_id(verification.document_back.path, verification):
#        return False
    from PIL import Image
    if not verification.document_back.name.split('.')[-1] == 'png':
        img = Image.open(verification.document_back.path)
        verification.document_back = str(verification.document_back.path) + '.png'
        img.save(verification.document_back.path, 'PNG')
        verification.save()
    if not verification.document_back_isolated:
        from verify.models import get_document_path
        new_path = os.path.join(settings.MEDIA_ROOT, get_document_path(verification, verification.document_back.name))
        from barcode.isolate import write_isolated
        write_isolated(verification.document_back.path, new_path)
        verification.document_back_isolated = new_path
        verification.save()
    import zxing
    reader = zxing.BarCodeReader()
    barcodes_raw = str(reader.decode(verification.document_back_isolated.path))
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
    if settings.USE_IDWARE and not decode_barcode(match, verification): return False
    processed = verification.barcode_data_processed
    if not text_matches_name(processed, verification.full_name) or not text_matches_birthday(processed, verification.birthday.strftime('%m/%d/%Y').replace('/', '')):
        print('mismatch')
        return False
    if not verification.document_number or len(verification.document_number) < 8 or not verification.document_number in processed:
        print('Number not found on document')
        return False
    return text_has_valid_birthday_and_expiry(verification.barcode_data_processed, '')
