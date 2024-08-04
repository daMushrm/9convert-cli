import requests
import click
from tqdm import tqdm
from colorama import Fore, Style, init
import os

init(autoreset=True)

BASE_URL = "https://9convert.com/api/ajaxSearch/index"
CONVERT_URL = "https://9convert.com/api/ajaxConvert/convert"
DOWNLOAD_DIR = "downloads"

ASCII_ART = """
  ___                        _        ___ _    ___ 
 / _ \__ ___ _ ___ _____ _ _| |_ ___ / __| |  |_ _|
 \_, / _/ _ \ ' \ V / -_) '_|  _|___| (__| |__ | | 
  /_/\__\___/_||_\_/\___|_|  \__|    \___|____|___|
                                                   
@ daMushrm
"""

def print_start_message():
    print(Fore.GREEN + ASCII_ART)

def fetch_video_info(video_url):
    print(Fore.CYAN + "Fetching video information...")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    payload = {
        'query': video_url,
        'vt': 'home'
    }
    response = requests.post(BASE_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def convert_video(vid, k):
    print(Fore.CYAN + "Converting video...")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    payload = {
        'vid': vid,
        'k': k
    }
    response = requests.post(CONVERT_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def download_file(url, filename):
    print(Fore.CYAN + f"Downloading {'audio' if filename.endswith('.mp3') else 'video'}...")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    with open(filepath, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        colour='green'
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = file.write(chunk)
            bar.update(size)
    print(Fore.GREEN + f"Downloaded: {filename}")

@click.command()
@click.argument('url')
@click.option('--format', default='mp4', help='Format to download the file in (mp4 or mp3).')
def cli(url, format):
    """
    A CLI tool to download YouTube videos using 9Convert.

    Arguments:
    URL     The URL of the YouTube video to download.

    Options:
    --format  Format to download the file in (default: mp4).
    """
    print_start_message()
    
    if format not in ['mp3', 'mp4']:
        print(Fore.RED + "Error: Invalid format. Please use either 'mp3' or 'mp4'.")
        return

    video_info = fetch_video_info(url)
    vid = video_info['vid']
    links = video_info['links'][format]
    print("Available qualities:")
    qualities = list(links.keys())
    for idx, quality in enumerate(qualities):
        info = links[quality]
        print(f"{idx + 1}: {quality}: {info['q']} ({info['size']})")
    
    chosen_quality_idx = click.prompt('Choose a quality', type=int)
    if chosen_quality_idx < 1 or chosen_quality_idx > len(qualities):
        print(Fore.RED + "Invalid quality choice. Exiting.")
        return
    
    chosen_quality = qualities[chosen_quality_idx - 1]
    k = links[chosen_quality]['k']
    conversion_info = convert_video(vid, k)
    download_url = conversion_info['dlink']
    filename = f"{conversion_info['title']}.{format}"
    download_file(download_url, filename)

if __name__ == "__main__":
    cli()
