import vk_api
import requests
import os
import re
import datetime
import sys

path_to_downloaded_albums = 'vk_downloaded_albums'
path_to_user_data = 'data.txt'
path_to_albums_list = 'albums_list.txt'


def print_progress(value, end_value, bar_length=20):
    percent = float(value) / end_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rProgress: [{0}] {1}% ({2} / {3})".format(
        arrow + spaces, int(round(percent * 100)),
        value, end_value))
    sys.stdout.flush()


def process_url(url):
    verification = re.compile(r'^https://vk.com/album(-?[\d]+)_([\d]+)$')
    o = verification.match(url)
    if not o:
        raise ValueError('invalid album link: {}'.format(url))
    owner_id = o.group(1)
    album_id = o.group(2)
    return {'owner_id': owner_id, 'album_id': album_id}


def read_data():
    lines = []
    try:
        with open(path_to_user_data, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError as e:
        print(e)
        print('please, fix the file name either in the folder or in the script')
        sys.exit(e.errno)

    if (lines.__len__() < 2):
    	print('unable to read login / phone number and password')
    	print('please, check your user data in the file')
    	sys.exit(1)
    l = lines[0]
    p = lines[1]

    queries = []
    try:
        with open(path_to_albums_list, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError as e:
        print(e)
        print('please, fix the file name either in the folder or in the script')
        sys.exit(e.errno)

    queries = []
    for url in lines:
        try:
            queries.append(process_url(url))
        except ValueError as e:
            print(e)
    return l, p, queries


def download_image(url, local_file_name):
    response = requests.get(url, stream=True)
    if not response.ok:
        print('bad response:', response)
        return
    with open(local_file_name, 'wb') as file:
        for chunk in response.iter_content(1024):
            # if not chunk:
            #     break
            file.write(chunk)
    return


def fix_illegal_album_title(title):
    illegal_character = '\/|:?<>*"'
    for c in illegal_character:
        title = title.replace(c, '_')
    return title


def main():
    l, p, queries = read_data()
    vk_session = vk_api.VkApi(l, p)

    try:
        vk_session.auth()
    except Exception as e:
        print('could not authenticate to vk.com')
        print(e)
        print('please, check your user data in the file')
        sys.exit(1)

    api = vk_session.get_api()
    l = None
    p = None

    print('number of albums to download: {}'.format(queries.__len__()))
    for q in queries:
        o = q['owner_id']
        a = q['album_id']

        try:
            album = api.photos.getAlbums(owner_id=o, album_ids=a)['items'][0]
            title = album['title']
            title = fix_illegal_album_title(title)
            images_num = album['size']
            photos = api.photos.get(owner_id=o, album_id=a, photo_sizes=1)['items']
        except vk_api.exceptions.ApiError as e:
            print('exception:')
            print(e)
            return

        album_path = path_to_downloaded_albums + '/' + title
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        else:
            album_path += '.copy_{:%Y-%m-%d_%H-%M-%S}'.format(
                datetime.datetime.now())
            os.makedirs(album_path)

        print('downloading album: ' + title)
        cnt = 0
        for p in photos:
            largest_image_width = p['sizes'][0]['width']
            largest_image_src = p['sizes'][0]['url']

            if largest_image_width == 0:
                largest_image_src = p['sizes'][p['sizes'].__len__() - 1]['url']
            else:
                for size in p['sizes']:
                    if size['width'] > largest_image_width:
                        largest_image_width = size['width']
                        largest_image_src = size['url']

            extension = re.findall(r'\.[\w\d.-]+$', largest_image_src)[0]
            download_image(largest_image_src, album_path + '/' +
                           str(p['id']) + extension)
            cnt += 1
            print_progress(cnt, images_num)
        print()


if __name__ == "__main__":
    main()
