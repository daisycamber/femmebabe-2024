import cv2
from shell.execute import run_command
from django.conf import settings
import numpy as np
import os, sys
from importlib import reload
from cv2 import dnn_superres
from importlib import import_module
from threading import Thread
import traceback
import math

SLICES = 50
SIMULTANEOUS_THREADS = 5

def superres(image_path, model, mode, size):
    run_command('sudo chmod a+rwX ' + str(image_path))
    run_command('sudo chmod {}:users '.format(settings.BASH_USER) + str(image_path))
    image = cv2.imread(image_path)
    height, width, dim = image.shape
    wmod = int(width/SLICES)
    hmod = int(height/SLICES)
    threads = [None] * (SLICES)
    images = [None] * SLICES
    dnn = [None] * SLICES
    def thread(image, y, images):
        print('superres slice {}'.format(y))
        try:
            image = cv2.imread(image_path)
            i = image[:, int(y * wmod):int((y + 1)*wmod)]
            path = os.path.join(settings.BASE_DIR, model)
            dnn[y] = import_module('cv2.dnn_superres')
            sr = dnn[y].DnnSuperResImpl_create()
            sr.readModel(path)
            sr.setModel(mode, size)
            result = sr.upsample(i)
            images[y] = result
        except:
            print(traceback.format_exc())
            thread(image, y, images)
    thread_count = 0
    last_threads = []
    while thread_count < SLICES:
        for i in range(SIMULTANEOUS_THREADS):
            threads[thread_count] = Thread(target=thread, args=(image, thread_count, images))
            threads[thread_count].start()
            thread_count = thread_count + 1
        for i in range(len(threads)):
            if threads[i]: threads[i].join()
    img = np.concatenate((images[0], images[1]), axis=1)
    for x in range(2,SLICES):
        img = np.concatenate((img, images[x]), axis=1)
    cv2.imwrite(image_path, img)

def superres_x8(image_path):
    superres(image_path, "enhance/LapSRN_x8.pb", 'lapsrn', 8)

def superres_x4(image_path):
    superres(image_path, "enhance/EDSR_x4.pb", 'edsr', 4)

def superres_x2(image_path):
    superres(image_path, "enhance/EDSR_x2.pb", 'edsr', 2)
