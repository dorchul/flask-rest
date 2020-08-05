import argparse
import logging

import flask

import data_model

_LOG_FMT = '%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s'

logger = logging.getLogger()
app = flask.Flask(__name__)
storage_manager = data_model.StorageManager()


@app.route('/api/v1/messages/<message_id>', methods=['GET'])
def read_message(message_id: str):
    try:
        message = storage_manager.read_message(message_id)
    except KeyError:
        return flask.make_response('unknown message_id', 400)
    return flask.jsonify(message.to_dict())


@app.route('/api/v1/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id: str):
    try:
        storage_manager.delete_message(message_id)
    except KeyError:
        return flask.make_response('unknown message_id', 400)
    return flask.make_response('', 200)


@app.route('/api/v1/messages', methods=['GET'])
def read_all():
    user_id = flask.request.args.get('user_id')
    if not user_id:
        return flask.make_response('user_id must be specified', 400)
    try:
        user = storage_manager.get_user(user_id)
    except KeyError:
        return flask.make_response('unknown user_id', 400)
    # for message in user.unread:
    #     storage_manager.read_message(message.message_id)
    messages = {
        'sent': [m.to_dict() for m in user.sent.values()],
        'read': [],
        'unread': [m.to_dict() for m in user.unread.values()],
    }
    unread_only = flask.request.args.get('unread_only') == '1'
    if not unread_only:
        messages['read'] = [m.to_dict() for m in user.read.values()]
    return flask.jsonify(messages)


@app.route('/api/v1/messages', methods=['POST'])
def write_message():
    data = flask.request.json
    if not data:
        return flask.make_response('missing request json data', 400)
    for arg in ['sender_id', 'receiver_id', 'subject', 'body']:
        if arg not in data:
            return flask.make_response(f'missing required arg: {arg}', 400)
    try:
        storage_manager.create_message(**data)
    except KeyError:
        return flask.make_response('invalid message params', 400)
    return flask.make_response('', 200)


def _add_debug_data():
    user1 = storage_manager.create_user()
    user2 = storage_manager.create_user()
    storage_manager.create_message(user1.user_id, user2.user_id, 'sub', 'body')


def main():
    logging.basicConfig(format=_LOG_FMT)
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--log-level',
                        choices=('debug', 'info', 'warning', 'error',
                                 'critical'),
                        default='warning')
    args = parser.parse_args()

    for handler in app.logger.handlers:
        handler.setFormatter(logging.Formatter(_LOG_FMT))
    logger.setLevel(getattr(logging, args.log_level.upper(), None))
    app.logger.setLevel(getattr(logging, args.log_level.upper(), None))

    if args.debug:
        app.debug = True
        _add_debug_data()

    try:
        app.run('localhost', port='8080', debug=args.debug)
    # pylint: disable=broad-except
    except Exception as e:
        app.logger.error('Caught exception: %s', e)
        # pylint: disable=import-outside-toplevel
        import pdb
        pdb.set_trace()


if __name__ == '__main__':
    main()
