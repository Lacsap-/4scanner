#!/usr/bin/env python3
import hashlib
import os

def hash_image(img_location):
    with open(img_location, 'rb') as img:
        m = hashlib.md5()
        while True:
            data = img.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def add_to_file(hash_file, img_hash):
    with open(hash_file, 'a') as f:
        f.write("{0}\n".format(img_hash))


def is_duplicate(hash_file, img_hash):
    if os.path.isfile(hash_file):
        with open(hash_file, "r") as f:
            for line in f:
                if img_hash in line:
                    return True

    return False


def hash_img_in_folder(folder, hash_file, check_duplicate):
    if check_duplicate:
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if os.path.isfile(os.path.join(folder, f)):
                    add_to_file(hash_file, hash_image(os.path.join(folder, f)))
    else:
        with open(hash_file, 'a') as f:
            f.write("not checking for duplicate\n")
