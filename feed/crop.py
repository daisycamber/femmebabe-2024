def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_center_half(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    top = int(img_height/4)
    lower = int(img_height/4) * 3
    return pil_img.crop(((img_width - crop_width) // 2,
                         top,
                         (img_width + crop_width) // 2,
                         lower))
