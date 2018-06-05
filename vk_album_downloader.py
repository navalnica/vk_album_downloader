import vk_api
import requests
import os
import re
import datetime
import sys


path_to_albums = 'd:/vk_downloaded_albums'


#   TODO
#   add only link to the album in data file


def print_progress(value, end_value, bar_length=20):
    percent = float(value) / end_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def read_data():
    with open('d:/data.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    l = lines[0]
    p = lines[1]
    num = int(lines[2])
    queries = []
    for x in range(num):
        queries.append({'owner_id': lines[3 + 2 * x], 'album_id': lines[3 + 2 * x + 1]})
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
    vk_session.auth()
    api = vk_session.get_api()

    for q in queries:
        g = q['owner_id']
        a = q['album_id']

        try:
            album = api.photos.getAlbums(owner_id='-' + g, album_ids=a)['items'][0]
            title = album['title']
            title = fix_illegal_album_title(title)
            images_num = album['size']
            photos = api.photos.get(owner_id='-' + g, album_id=a, photo_sizes=1)['items']
        except vk_api.exceptions.ApiError as e:
            print('exception:')
            print(e)
            return

        album_path = path_to_albums + '/' + title
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        else:
            album_path += '.copy_{:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())
            os.makedirs(album_path)

        print('downloading album: ' + title)
        cnt = 0
        for p in photos:
            biggest = p['sizes'][0]['width']
            biggest_src = p['sizes'][0]['src']
            for size in p['sizes']:
                if size['width'] > biggest:
                    biggest = size['width']
                    biggest_src = size['src']

            extension = re.findall(r'\.[\w\d.-]+$', biggest_src)[0]
            download_image(biggest_src, album_path + '/' + str(p['id']) + extension)
            cnt += 1
            print_progress(cnt, images_num)
        print('')


if __name__ == "__main__":
    main()
