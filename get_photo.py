import urllib.request,urllib.error

photo_file = "photos/1.jpg"
path="https://img2.doubanio.com/view/photo/s_ratio_poster/public/p479682972.webp"
head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/99.0.4844.51 Safari/537.36"
}
urllib.request.urlretrieve(path, photo_file)