import requests


def get_book_cover(book_title):
    # api_key = 'YOUR_GOOGLE_BOOKS_API_KEY'
    url = f"https://www.googleapis.com/books/v1/volumes?q=book_title:{book_title}"  # isbn:{isbn}'  # &key={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            image_link = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            return image_link
    return None
