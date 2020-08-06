import datetime
import logging
import threading
import uuid
from typing import Dict

logger = logging.getLogger()


class User:

    def __init__(self, user_id):
        self.user_id = user_id
        self.sent = {}
        self.unread = {}
        self.read = {}

    def to_dict(self) -> Dict[str, str]:
        return {'id': self.user_id}


class Message:

    # pylint: disable=too-many-arguments
    def __init__(self, message_id: str, sender: User, receiver: User,
                 subject: str, body: str):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.creation_date = datetime.datetime.utcnow()

    def to_dict(self) -> Dict[str, str]:
        return {
            'sender': self.sender.user_id,
            'receiver': self.receiver.user_id,
            'subject': self.subject,
            'body': self.body,
            'creation_date': self.creation_date
        }


class StorageManager:

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._messages: Dict[str, Message] = {}
        self._lock = threading.Lock()

    def get_user(self, user_id: str) -> User:
        with self._lock:
            return self._users[user_id]

    def create_user(self) -> User:
        user_id = uuid.uuid4().hex[:6]
        logger.debug('Creating user with id: %s', user_id)
        user = User(user_id)
        with self._lock:
            self._users[user_id] = user
        return user

    def read_message(self, message_id: str) -> Message:
        with self._lock:
            message = self._messages[message_id]
            if message.message_id in message.receiver.unread:
                del message.receiver.unread[message.message_id]
                message.receiver.read[message_id] = message
            return message

    def create_message(self, sender_id, receiver_id, subject, body) -> Message:
        with self._lock:
            sender = self._users[sender_id]
            receiver = self._users[receiver_id]
            message_id = uuid.uuid4().hex[:6]
            logger.debug('Creating message with id: %s', message_id)
            message = Message(message_id, sender, receiver, subject, body)
            self._messages[message_id] = message
            self._users[sender_id].sent[message_id] = message
            self._users[receiver_id].unread[message_id] = message
        return message

    def delete_message(self, message_id: str) -> None:
        with self._lock:
            message = self._messages[message_id]
            del self._messages[message_id]
            del message.sender.sent[message_id]
            if message_id in message.receiver.read:
                del message.receiver.read[message_id]
            if message_id in message.receiver.unread:
                del message.receiver.unread[message_id]
