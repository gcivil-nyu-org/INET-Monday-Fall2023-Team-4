from channels.testing import WebsocketCommunicator
from django.test import TestCase
from channels.routing import URLRouter
from django.urls import path
from .consumers import ChatConsumer  # Import your ChatConsumer here

class ChatConsumerTest(TestCase):
    def setUp(self):
        # Define an in-memory channel layer for testing
        self.channel_layer = get_channel_layer()
        self.application = URLRouter([
            path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
        ])

    async def test_websocket_connection(self):
        # Establish a connection to the WebSocket
        communicator = WebsocketCommunicator(self.application, "/ws/chat/testroom/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        # Disconnect
        await communicator.disconnect()

    async def test_send_receive_message(self):
        # Establish a connection to the WebSocket
        communicator = WebsocketCommunicator(self.application, "/ws/chat/testroom/")
        await communicator.connect()

        # Send a message to the WebSocket
        await communicator.send_json_to({"message": "Hello", "username": "testuser"})

        # Receive the response from the WebSocket
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"message": "Hello", "username": "testuser"})

        # Disconnect
        await communicator.disconnect()

    async def test_disconnect(self):
        # Establish a connection to the WebSocket
        communicator = WebsocketCommunicator(self.application, "/ws/chat/testroom/")
        await communicator.connect()

        # Disconnect
        await communicator.disconnect()

        # Test if the WebSocket is closed
        self.assertFalse(communicator.connected)


class ChatViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get('/chat/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/index.html')

    def test_room_view(self):
        room_name = 'testroom'
        response = self.client.get(f'/chat/{room_name}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room.html')
        self.assertEqual(response.context['room_name'], room_name)
