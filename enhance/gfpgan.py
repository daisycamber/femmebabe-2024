from shell.execute import run_command
import shutil
import os
from django.conf import settings
import gc
import torch

base_dir = os.path.join(settings.BASE_DIR, 'temp/gfpgan/')
op_dir = os.path.join(settings.BASE_DIR, 'temp/gfpgan-output/')
op_extra = 'restored_imgs/'
extra_dirs = ['cmp/', 'restored_faces/', 'cropped_faces/', 'restored_imgs/']

def gfpgan_enhance(image_path):
    gc.collect()
    torch.cuda.empty_cache()
    os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'max_split_size_mb:512')
    filename = image_path.split('/')[-1]
    path = os.path.join(base_dir, filename)
    shutil.copy(image_path, path)
    print(run_command('venv/bin/python GFPGAN/inference_gfpgan.py -i {} -o {} -v 1.3 -s 2'.format(base_dir, op_dir)))
    dest_path = os.path.join(op_dir, op_extra, filename)
    try:
        for f in os.listdir(base_dir):
            os.remove(os.path.join(base_dir, f))
        shutil.copy(dest_path, image_path)
        for dir in extra_dirs:
            for f in os.listdir(os.path.join(op_dir, dir)):
                os.remove(os.path.join(op_dir, dir, f))
    except: pass
