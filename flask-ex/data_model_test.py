import pytest

import data_model


def _create_manager_with_simple_message(subject, body):
    manager = data_model.StorageManager()
    user1 = manager.create_user()
    user2 = manager.create_user()
    message = manager.create_message(user1.user_id, user2.user_id, subject,
                                     body)
    return manager, message


def test_create_and_get_user():
    manager = data_model.StorageManager()
    user = manager.create_user()
    manager.get_user(user.user_id)


def test_create_multiple_users():
    manager = data_model.StorageManager()
    users = []
    for _ in range(10):
        users.append(manager.create_user())
    # Verify user_ids are unique
    assert len(set(u.user_id for u in users)) == 10


def test_create_message():
    _, message = _create_manager_with_simple_message('sub', 'body')
    assert len(message.sender.sent) == 1
    assert len(message.receiver.unread) == 1
    assert message.subject == 'sub'
    assert message.body == 'body'


def test_read_message():
    manager, message = _create_manager_with_simple_message('sub', 'body')
    assert len(message.receiver.read) == 0
    assert len(message.receiver.unread) == 1
    manager.read_message(message.message_id)
    assert len(message.receiver.read) == 1
    assert len(message.receiver.unread) == 0


def test_delete_message():
    manager, message = _create_manager_with_simple_message('sub', 'body')
    manager.delete_message(message.message_id)
    assert len(message.sender.sent) == 0
    assert len(message.receiver.unread) == 0
    with pytest.raises(KeyError):
        manager.read_message(message.message_id)

        
