FREQUENCY = 200
AVERAGE = 100
EXTRA = 1
MIN_TEXT = 4

def censor_video(input_file, output_file, scale=1):
    import cv2, pytesseract
    import numpy as np
    from moviepy.editor import *
    clip = VideoFileClip(input_file)
    vidcap = cv2.VideoCapture(input_file)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, FREQUENCY)
    index = 0
    while has_frames:
        has_frames, image = vidcap.read()
        if has_frames:
            dim = (int(image.shape[0] * scale), int(image.shape[1] * scale), image.shape[2])
            small_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            transparent_img = np.zeros((image.shape[0], image.shape[1], image.shape[2]), dtype=np.uint8)
            data = pytesseract.image_to_data(small_image, output_type='dict')
            boxes = len(data['level'])
            for i in range(boxes):
                if len(data['text']) < MIN_TEXT: continue
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                x = int(x / scale)
                y = int(y / scale)
                w = int(w / scale)
                h = int(h / scale)
                x = x - w * extra
                y = y - h * extra
                w = w * extra * 3
                h = h * extra * 3
                if x < 0: x = 0
                if y < 0: y = 0
                if y + h > image.shape[0]: y = image.shape[0] - h
                if x + w > image.shape[1]: x = image.shape[1] - w
                img = cv2.blur(image[y:y+h, x:x+w], (AVERAGE, AVERAGE))
                transparent_img[y:y+h, x:x+w] = img
                im = ImageClip(transparent_img, duration=FREQUENCY/1000.0)
                clip = CompositeVideoClip([clip, im.set_start(index * FREQUENCY).set_duration(FREQUENCY)])
        index = index + 1
    clip.write_videofile(output_path)
