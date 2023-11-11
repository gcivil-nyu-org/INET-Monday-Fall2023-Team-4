from channels.testing import WebsocketCommunicator
import pytest
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import ChatConsumer  # Import your ChatConsumer here
from django.test import TestCase, Client
from django.urls import reverse


# Use pytest's asynchronous capabilities
@pytest.mark.asyncio
class ChatConsumerTest:
    async def test_websocket_connection(self):
        # Setup the application to be tested
        application = ProtocolTypeRouter({
            "websocket": URLRouter([
                path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
            ])
        })

        # Create a WebsocketCommunicator instance for the test
        communicator = WebsocketCommunicator(application, "ws/chat/testroom/")

        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Disconnect from the WebSocket
        await communicator.disconnect()

    async def test_send_receive_message(self):
        application = ProtocolTypeRouter({
            "websocket": URLRouter([
                path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
            ])
        })

        communicator = WebsocketCommunicator(application, "ws/chat/testroom/")
        await communicator.connect()

        # Send a message
        await communicator.send_json_to({"message": "Hello", "username": "testuser"})

        # Receive and assert the response
        response = await communicator.receive_json_from()
        assert response == {"message": "Hello", "username": "testuser"}

        await communicator.disconnect()

    async def test_disconnect(self):
        application = ProtocolTypeRouter({
            "websocket": URLRouter([
                path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
            ])
        })

        communicator = WebsocketCommunicator(application, "ws/chat/testroom/")
        await communicator.connect()
        await communicator.disconnect()

        # Check if the WebSocket is closed
        assert not communicator.connected


class ChatViewsTest(TestCase):
    def setUp(self):
        # Django test client
        self.client = Client()

    def test_index_view(self):
        # Test the index view
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/index.html')

    def test_room_view(self):
        # Test the room view with a sample room name
        room_name = 'testroom'
        response = self.client.\
            get(reverse('room', kwargs={'room_name': room_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room.html')
        self.assertEqual(response.context['room_name'], room_name)
