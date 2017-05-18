#!/usr/bin/env python3

import argparse
from scanner import chan_info, dupecheck
import json
import logging
import os
import sys
import re
import time
import urllib
import http.client
import requests
import threading
import shutil


def load(url, downloaded_log, img_hash_log, is_quiet):
    response = requests.get(url)
    if response.status_code == 404:
        if not is_quiet:
            print('thread 404\'d')
        remove_tmp_files(img_hash_log, downloaded_log)
        exit(0)
    return response.text


def create_dir(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:  # folder may have been created by other threads
            if e.errno != 17:
                print("Cannot create {0}".format(directory))
                exit(1)
            pass


def add_to_downloaded_log(img_filename, downloaded_log):
    f = open(downloaded_log, "a")
    f.write("{0}\n".format(img_filename))
    f.close()


def was_downloaded(img_filename, downloaded_log):
    if os.path.isfile(downloaded_log):
        f = open(downloaded_log, "r")
        if str(img_filename) in f.read():
            f.close()
            return True
        else:
            return False
    else:
        return False


def extension_condition(condition_ext, post_ext):
    if condition_ext:
        for extension in condition_ext:
            if extension == post_ext:
                return True
    else:
        # Always return true if condition was not specified
        return True

    return False


def filename_condition(condition_filename, post_filename):
    if condition_filename:
        for i in condition_filename:
            if i.lower() in post_filename.lower():
                return True
    else:
        # Always return true if condition was not specified
        return True

    return False


def width_condition(condition_width, post_width):
    if condition_width:
        if condition_width[0] == "=":
            if int(post_width) == int(condition_width.split("=")[-1]):
                return True
        elif condition_width[0] == "<":
            if int(post_width) < int(condition_width.split("<")[-1]):
                return True
        elif condition_width[0] == ">":
            if int(post_width) > int(condition_width.split(">")[-1]):
                return True
        else:
            print("width need to be in this format:")
            print(">1024, <256 or =1920")
            exit(1)
    else:
        # Always return true if condition was not specified
        return True

    return False


def height_condition(condition_height, post_height):
    if condition_height:
        if condition_height[0] == "=":
            if int(post_height) == int(condition_height.split("=")[-1]):
                return True
        elif condition_height[0] == "<":
            if int(post_height) < int(condition_height.split("<")[-1]):
                return True
        elif condition_height[0] == ">":
            if int(post_height) > int(condition_height.split(">")[-1]):
                return True
        else:
            print("height need to be in this format:")
            print(">1024, <256 or =1080")
            exit(1)
    else:
        # Always return true if condition was not specified
        return True

    return False


# Check if all condition returned true
def all_condition_check(condition_list):
    for i in condition_list:
        if not i:
            return False
    return True


# Return True if an image fit all search conditions
def meet_dl_condition(post, condition):
    condition_list = []
    condition_list.append(extension_condition(condition["ext"], post['ext']))
    condition_list.append(width_condition(condition["width"], post['w']))
    condition_list.append(height_condition(condition["height"], post['h']))
    condition_list.append(filename_condition(condition["filename"], post['filename']))
    return all_condition_check(condition_list)


def remove_if_duplicate(img_path, img_hash_log):
    if img_path:
        img_hash = dupecheck.hash_image(img_path)
        if dupecheck.is_duplicate(img_hash_log, img_hash):
            os.remove(img_path)
            return True
        else:
            dupecheck.add_to_file(img_hash_log, img_hash)
            return False


def remove_tmp_files(img_hash_log, downloaded_log):
    if os.path.isfile(img_hash_log):
        os.unlink(img_hash_log)

    if os.path.isfile(downloaded_log):
        os.unlink(downloaded_log)


# Return downloaded picture URL or false if an error occured
def download_image(image_url, post_dic, dl_dir):
    try:
        pic_url = image_url + str(post_dic["tim"]) + post_dic["ext"]
        out_pic = os.path.join(dl_dir, str(post_dic["tim"]) + post_dic["ext"])
        urllib.request.urlretrieve(pic_url, out_pic)
    except urllib.error.HTTPError as err:
        return False

    return out_pic


def download_thread(thread_nb, board, chan, output_folder, folder, is_quiet, condition, check_duplicate):

    # Getting info about the chan URL
    chan_url_info = chan_info.get_chan_info(chan)
    if not chan_url_info:
        print("{0} does not exist or is not supported.".format(chan))
        exit(1)
    base_url = chan_url_info[0]
    image_url = chan_url_info[3]
    thread_subfolder = chan_url_info[1]
    image_subfolder = chan_url_info[2]

    # These URL are the url of the thread
    # and the base url where images are stored on the imageboard
    thread_url = "{0}{1}{2}{3}.json".format(base_url, board, thread_subfolder, thread_nb)
    image_url = "{0}{1}{2}".format(image_url, board, image_subfolder)

    tmp_dir = "/tmp/{0}/".format(os.getpid())
    curr_time = time.strftime('%d%m%Y-%H%M%S')
    pid = os.getpid()
    thread = threading.current_thread().name

    downloaded_log = "{0}/{1}4scanner_dld-{2}-{3}".format(tmp_dir, curr_time, pid, thread)
    img_hash_log = "{0}/{1}4scanner_hash-{2}-{3}".format(tmp_dir, curr_time, pid, thread)

    out_dir = os.path.join(output_folder, 'downloads', chan, board, folder)

    create_dir(tmp_dir)
    create_dir(out_dir)

    # Fill the hash_log file with hash from image already in the dir
    dupecheck.hash_img_in_folder(out_dir, img_hash_log, check_duplicate)

    # Main download code
    while True:
        # Getting the thread's json
        try:
            thread_json = json.loads(load(thread_url, downloaded_log, img_hash_log, is_quiet))
        except ValueError:
            print("Problem connecting to {0}. stopping download for thread {1}".format(chan, thread_nb))
            remove_tmp_files(img_hash_log, downloaded_log)
            exit(1)

        # Image download loop
        for post in thread_json["posts"]:
            if 'filename' in post:
                if not was_downloaded(post["tim"], downloaded_log):
                    if meet_dl_condition(post, condition):
                        tmp_pic = download_image(image_url, post, tmp_dir)
                        final_pic = os.path.join(out_dir, tmp_pic.split('/')[-1])
                        add_to_downloaded_log(post["tim"], downloaded_log)

                        if check_duplicate:
                            # If picture is not a duplicate copy it to out_dir
                            if not remove_if_duplicate(tmp_pic, img_hash_log):
                                shutil.move(tmp_pic, final_pic)
                        else:
                            shutil.move(tmp_pic, final_pic)

                        time.sleep(2)

            # Some imageboards allow more than 1 picture per post
            if 'extra_files' in post:
                for picture in post["extra_files"]:
                    if not was_downloaded(picture["tim"], downloaded_log):
                        if meet_dl_condition(picture, condition):
                            tmp_pic = download_image(image_url, picture, tmp_dir)
                            final_pic = os.path.join(out_dir, tmp_pic.split('/')[-1])
                            add_to_downloaded_log(picture["tim"], downloaded_log)

                            if check_duplicate:
                                # If picture is not a duplicate copy it to out_dir
                                if not remove_if_duplicate(tmp_pic, img_hash_log):
                                    shutil.move(tmp_pic, final_pic)
                            else:
                                shutil.move(tmp_pic, final_pic)


                            time.sleep(2)
        if not is_quiet:
            print('.')
        time.sleep(20)
