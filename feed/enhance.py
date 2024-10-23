
def enhance(image_path):
    from image_enhancement import image_enhancement
    import cv2
    input = cv2.imread(image_path)
    ie = image_enhancement.IE(input, 'HSV')
    output = ie.GHE()
    cv2.imwrite(image_path, output)
