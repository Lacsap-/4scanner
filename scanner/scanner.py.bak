#!/usr/bin/env python3

import time
import json
import os
import re
from scanner import download, chan_info
import subprocess
import urllib.request
import threading
import http.client


def get_catalog_json(board, chan):
    chan_base_url = chan_info.get_chan_info(chan)[0]
    catalog = urllib.request.urlopen(
              "{0}{1}/catalog.json".format(chan_base_url, board))
    try:
        catalog_data = catalog.read()
    except http.client.IncompleteRead as err:
        catalog_data = err.partial
    return json.loads(catalog_data.decode("utf8"))


def scan_thread(keyword, catalog_json):
    # Check each thread, threads who contains the keyword are returned
    matched_threads = []
    for i in range(len(catalog_json)):
        for thread in catalog_json[i]["threads"]:
            regex = r'\b{0}\b'.format(keyword)
            # Search thread title
            if 'sub' in thread:
                if re.search(regex, str(thread["sub"]), re.IGNORECASE):
                    matched_threads.append(thread["no"])

            # Search OPs post body
            if 'com' in thread:
                if re.search(regex, str(thread["com"]), re.IGNORECASE):
                    matched_threads.append(thread["no"])

    return matched_threads


def download_thread(thread_id, chan, board, folder, output, condition, dupe_check):
    t = threading.Thread(target=download.download_thread, args=(thread_id,
                                                                board,
                                                                chan,
                                                                output,
                                                                folder,
                                                                True,
                                                                condition,
                                                                dupe_check))
    t.daemon = True
    t.start()


def add_to_downloaded(id, log_file, output):
    download_log = open("{0}/{1}".format(output, log_file), "a")
    download_log.write("{0}\n".format(id))


def folder_size_mb(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / 1000000


def check_quota(folder, quota_mb):
    if int(quota_mb) < folder_size_mb(os.path.join(folder, "downloads")):
        print("Quota limit exceeded. Stopping 4scanner.")
        exit(0)


def get_check_duplicate(search):
    if 'check_duplicate' in search:
        if search['check_duplicate']:
            return True
        else:
            return False

    # duplicate check is on by default
    return True

def get_condition(search):
    condition = {}
    if 'extension' in search:
        condition["ext"] = []
        if isinstance(search['extension'], str):
            condition["ext"].append(search['extension'])
        else:
            for extension in search['extension']:
                condition["ext"].append(extension)
    else:
        condition["ext"] = False

    if 'filename' in search:
        condition["filename"] = []
        if isinstance(search['filename'], str):
            condition["filename"].append(search['filename'])
        else:
            for extension in search['filename']:
                condition["filename"].append(extension)
    else:
        condition["filename"] = False

    if 'width' in search:
        condition["width"] = search['width']
    else:
        condition["width"] = False

    if 'height' in search:
        condition["height"] = search['height']
    else:
        condition["height"] = False

    return condition


def get_imageboard(search):
    if 'imageboard' in search:
        chan = search["imageboard"]
        if not chan_info.get_chan_info(chan):
            print("{0} is not supported.".format(chan))
            exit(1)
    else:
        # default
        chan = "4chan"

    return chan


def get_keyword(search):
    if 'keywords' in search:
        keywords_array = []
        if isinstance(search['keywords'], str):
            keywords_array.append(search['keywords'])
        else:
            for keywords in search['keywords']:
                keywords_array.append(keywords)
    else:
        print("Cannot scan without any keyword...")
        exit(1)

    return keywords_array


def scan(keywords_file, output, log_file, quota_mb, wait_time):
    while True:
        if quota_mb:
            check_quota(output, quota_mb)

        curr_time = time.strftime('%d%b%Y-%H%M%S')
        print("{0} Searching threads...".format(curr_time))

        dl_log = open("{0}/{1}".format(output, log_file), "a")
        dl_log.write(time.strftime('Execution date {0}\n'.format(curr_time)))
        dl_log.close()

        try:
            json_file = json.load(open(keywords_file))
        except ValueError:
            print("Your JSON file is malformed. Quitting.")
            exit(1)

        for search in json_file["searches"]:
            # Getting imageboard to search
            chan = get_imageboard(search)
            # Checking conditions
            condition = get_condition(search)
            # Check if we need to check for duplicate when downloading
            dupe_check = get_check_duplicate(search)
            # Getting output folder name
            folder_name = search["folder_name"]
            board = search["board"]
            keywords = get_keyword(search)

            try:
                catalog_json = get_catalog_json(board, chan)

                for keyword in keywords:
                    threads_id = scan_thread(keyword, catalog_json)

                    dl_log = open("{0}/{1}".format(output, log_file)).read()
                    for thread_id in list(set(threads_id)):
                        if str(thread_id) not in dl_log:
                            download_thread(thread_id, chan, board,
                                            folder_name,
                                            output,
                                            condition, dupe_check)
                            add_to_downloaded(thread_id, log_file, output)
            except urllib.error.HTTPError as err:
                print("Error while opening {0} catalog page. "
                      "Retrying during next scan.".format(board))
                pass

        active_downloads = threading.active_count()-1
        print("{0} threads currently downloading.".format(active_downloads))
        print("Searching again in {0} minutes!"
              .format(str(int(wait_time / 60))))
        time.sleep(wait_time)
