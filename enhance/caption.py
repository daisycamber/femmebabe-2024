import re
#import streamlit as st
from PIL import Image
#from tqdm import tqdm
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image
#from tqdm import tqdm
import urllib.request
from itertools import cycle
import os
from django.conf import settings
from feed.models import Post

TF_URL = "https://app.truefoundry.com/"

replace = {'man': 'woman', 'boy': 'woman', 'his': 'her', 'man\'s': 'woman\'s', 'men': 'women', 'him': 'her', 'beard': 'piercing', 'knife': 'pose', 'mustache': 'makeup', 'a makeup': 'makeup', 'with makeup': 'wearing makeup', 'dog': 'phone'}

def caption_image(image_path):
    os.environ['MLF_HOST'] = TF_URL
    os.environ['MLF_API_KEY'] = settings.TF_API_KEY
    model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    device = torch.device("cpu") #"cuda" if torch.cuda.is_available() else 
    model.to(device)
    max_length = 16
    num_beams = 4
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
    caption_text = " "
    images = []
    i_image = Image.open(image_path)
    if i_image.mode != "RGB":
        i_image = i_image.convert(mode="RGB")
    images.append(i_image)
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    output_ids = model.generate(pixel_values)
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    predicted_captions = preds
    for i,caption in enumerate(predicted_captions):
        caption_text = caption_text + caption
    for key, value in replace.items():
        caption_text = re.sub('\s' + key + '\s', ' ' + value + ' ', caption_text)
        caption_text = re.sub('\s' + key + '\.', ' ' + value + '.', caption_text)
        caption_text = re.sub('\s' + key + '\,', ' ' + value + ',', caption_text)
    return caption_text.strip().capitalize() + ('.' if not caption_text[-1] == '.' else '')

def caption_post(post):
    print(post.id)
    if post.uploaded:
        if post.image:
            try:
                if not os.path.exists(post.image.path) and (post.image or post.image_bucket): post.download_photo()
            except: post.download_photo()
            post = Post.objects.get(id=post.id)
            if post.image and os.path.exists(post.image.path):
                try:
                    post.content = caption_image(post.image.path)
                except: pass
            if post.image_bucket:
                try:
                    os.remove(post.image.path)
                except: pass
            post.save()
            print(post.content)
            return post.content
    return None

def routine_caption_image():
    print('Captioning image')
    for post in Post.objects.filter(content='', public=True).exclude(image=None).order_by('-date_posted'):
        if post.image:
            p = caption_post(post)
            if p: return
    for post in Post.objects.filter(content='', public=False).exclude(image=None).order_by('-date_posted'):
        if post.image:
            caption_post(post)
            if p: return
