import requests


def get_book_cover(book):
    if book.isbn is not None:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{book.isbn}"
    else:
        url = f"https://www.googleapis.com/books/v1/volumes?q=book_title:{book.title}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            image_link = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            return image_link
    return None
