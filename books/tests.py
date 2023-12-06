from django.test import TestCase, RequestFactory
from user.models import CustomUser
from .models import Book, Rating
from django.urls import reverse
from .views import BookDetailView, rate_book
import unittest
from unittest.mock import patch
from .utils import get_book_cover


class BookModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", isbn=123456789
        )

    def test_book_str_method(self):
        self.assertEqual(str(self.book), "Test Book")

    def test_average_rating_method_with_no_ratings(self):
        self.assertEqual(self.book.average_rating(), 0)

    def test_average_rating_method_with_ratings(self):
        Rating.objects.create(user=self.user, book=self.book, value=4)
        Rating.objects.create(user=self.user, book=self.book, value=2)

        self.assertEqual(self.book.average_rating(), 3)


class RatingModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", isbn=123456789
        )

    def test_rating_str_method(self):
        rating = Rating.objects.create(user=self.user, book=self.book, value=4)
        self.assertEqual(str(rating), "Test Book - 4 stars")

    def test_rating_default_value(self):
        rating = Rating.objects.create(user=self.user, book=self.book)
        self.assertEqual(rating.value, 0)

    def test_rating_choices(self):
        for i in range(1, 6):
            rating = Rating.objects.create(user=self.user, book=self.book, value=i)
            self.assertEqual(rating.value, i)


class BookDetailViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", isbn=123456789
        )
        self.rating = Rating.objects.create(user=self.user, book=self.book, value=4)

    def test_book_detail_view(self):
        factory = RequestFactory()
        request = factory.get(reverse("book_detail", args=[self.book.pk]))
        response = BookDetailView.as_view()(request, pk=self.book.pk)
        self.assertEqual(response.status_code, 200)


class RateBookViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", isbn=123456789
        )

    def test_rate_book_view_with_valid_rating(self):
        factory = RequestFactory()
        request = factory.post(
            reverse("rate_book", args=[self.book.pk]), {"rating": "3"}
        )
        request.user = self.user
        response = rate_book(request, pk=self.book.pk)
        self.assertEqual(response.status_code, 302)  # Redirect after successful rating

        # Check if the rating was added to the database
        rating = Rating.objects.get(user=self.user, book=self.book)
        self.assertEqual(rating.value, 3)

    def test_rate_book_view_with_invalid_rating(self):
        factory = RequestFactory()
        request = factory.post(
            reverse("rate_book", args=[self.book.pk]), {"rating": "invalid"}
        )
        request.user = self.user
        response = rate_book(request, pk=self.book.pk)
        self.assertEqual(response.status_code, 400)  # Bad Request due to invalid rating

        # Check if the rating was not added to the database
        with self.assertRaises(Rating.DoesNotExist):
            Rating.objects.get(user=self.user, book=self.book)

    def test_rate_book_view_with_invalid_method(self):
        factory = RequestFactory()
        request = factory.get(reverse("rate_book", args=[self.book.pk]))
        response = rate_book(request, pk=self.book.pk)
        self.assertEqual(response.status_code, 400)


class GetBookCoverTests(unittest.TestCase):
    @patch("requests.get")
    def test_get_book_cover_with_isbn(self, mock_requests_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "volumeInfo": {
                        "imageLinks": {"thumbnail": "https://example.com/thumbnail.jpg"}
                    }
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        class MockBook:
            isbn = "123456789"
            title = None

        book = MockBook()
        result = get_book_cover(book)
        self.assertEqual(result, "https://example.com/thumbnail.jpg")

    @patch("requests.get")
    def test_get_book_cover_with_title(self, mock_requests_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "volumeInfo": {
                        "imageLinks": {"thumbnail": "https://example.com/thumbnail.jpg"}
                    }
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        class MockBook:
            isbn = None
            title = "Test Book"

        book = MockBook()
        result = get_book_cover(book)
        self.assertEqual(result, "https://example.com/thumbnail.jpg")

    @patch("requests.get")
    def test_get_book_cover_no_data(self, mock_requests_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_requests_get.return_value = mock_response

        class MockBook:
            isbn = "123456789"
            title = None

        book = MockBook()
        result = get_book_cover(book)
        self.assertIsNone(result)

    @patch("requests.get")
    def test_get_book_cover_request_error(self, mock_requests_get):
        mock_requests_get.side_effect = mock_requests_get.RequestException(
            "Mocked error"
        )

        class MockBook:
            isbn = "123456789"
            title = None

        book = MockBook()
        result = get_book_cover(book)
        self.assertIsNone(result)
