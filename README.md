# vk_album_downloader
Python script to download list of albums (including albums from private communities) from [vk.com](https://www.vk.com). Implemented with VK API

## Installation ##
In order to use this script you need to install [Python 3](https://www.python.org/downloads/).

You also need additional **vk_api** module. Write next command to your command line / terminal after you have installed Python 3

`$ pip install vk_api`

## Usage ##
This script allows you to download:
* Albums from user's profile
* Albums from communities, including private communities

**NOTE:** script yet can not download any special albums such as 'Saved images', 'Profile images', 'Images from wall'

You have to create following files to gather input information:
* *data.txt*. (Because of the *vk.com* privacy policy script needs to perform authentication before interacting with VK API. So put your login / phone number and password into this file)
* *albums_list.txt* (Just put list of url to the albums that you want do download)

Script will automatically create directory **vk_downloaded_albums** to save albums to in the directory where the script is located

**NOTE:** all the file / directory names and paths can be modified in the script. There is also no need to put them in the directory with the script

## Examples of the input files ##

### data.txt ###
File with user data:

```
test@gmail.com
super_strong_password
```

### albums_list.txt ###
File with list of album URLs:

```
https://vk.com/album-23402051_225962711
https://vk.com/album-23402051_249165407
```
