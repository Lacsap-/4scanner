#!/usr/bin/env python3

def get_chan_info(chan):
    if chan == "4chan":
        # 4chan informations
        chan_base_url = "http://a.4cdn.org/"
        chan_image_base_url = "http://i.4cdn.org/"
        chan_thread_subfolder = "/thread/"
        chan_image_subfolder = "/"
    elif chan == "lainchan":
        # lainchan informations
        chan_base_url = "https://lainchan.org/"
        chan_image_base_url = "https://lainchan.org/"
        chan_thread_subfolder = "/res/"
        chan_image_subfolder = "/src/"
    elif chan == "uboachan":
        # uboachan informations
        chan_base_url = "https://uboachan.net/"
        chan_image_base_url = "https://uboachan.net/"
        chan_thread_subfolder = "/res/"
        chan_image_subfolder = "/src/"
    else:
        return False

    return [chan_base_url, chan_thread_subfolder, chan_image_subfolder,
            chan_image_base_url]
