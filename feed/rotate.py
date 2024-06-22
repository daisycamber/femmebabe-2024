def rotate(image_path, direction):
    from PIL import Image
    img = Image.open(image_path)
    img = img.rotate(90 * direction, expand=True)
    img.save(image_path)
