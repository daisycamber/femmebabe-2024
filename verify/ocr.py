def get_image_text(path, lang='eng'):
    import cv2
    import pytesseract
    from PIL import Image
    print('Trying to tesseract (ocr) image')
    image = Image.open(path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
        image.save(path)
#    img_cv = cv2.imread(path)
#    mode = Image.open(path).mode[0]
#    img = img_cv
#    if mode == 'B':
#        img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(image, lang=lang)
    print(text)
    return text
