from datetime import datetime

from flask import Blueprint, render_template, current_app, request
from flask_login import current_user
from flask_socketio import emit, join_room, rooms, leave_room

from app.extends import socketio, db, logger
from app.forms import RoomForm
from app.models import Message, User

chat_bp = Blueprint('chat', __name__)
online_users = []
user_to_sid = {}  # 映射username to session.id
sid_to_user = {}


@chat_bp.route('/')
def home():
    form = RoomForm()
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name='chat').order_by(Message.timestamp.asc())[-amount:]

    return render_template('home.html', messages=messages, form=form, mode=1)


# AJAX message interface
@chat_bp.route('/chatroom/<room_name>', methods=['GET'])
def room_message(room_name):
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name=room_name).order_by(Message.timestamp.asc())[-amount:]
    return render_template('chat/_messages.html', messages=messages, mode=1)


# experimental p2p chat
@chat_bp.route('/p/<username>')
def private_chat(username):
    # return redirect('http://127.0.0.1/p/' + uuid)
    sid = user_to_sid[username]
    # BUG: User A and B will both join the room opposite, so one con only see
    # messages sent by himself. In order to receive messages, he must back to
    # his private room. What's more, if more than one user send private
    # messages to A, A will see messages from different users are mixed.
    # So such a feature is like a message board instead of a private p2p chat.
    # TODO: Use a (id, id) pair as the identifier of a p2p room
    return room_message(sid)


# user about
@chat_bp.route('/a/<username>')
def user_about(username):
    about = getUserFromUsername(username).about
    data = {'about': about, 'sid': user_to_sid[username]}
    return data


@socketio.on('connect')
def connect():
    global online_users
    user = current_user._get_current_object()
    if current_user.is_authenticated and user not in online_users:
        online_users.append(user)
        user_to_sid[user.username] = request.sid
        sid_to_user[request.sid] = user.username
        logger.info("%s is connected." % user.username)
    logger.info("online users: {}".format(online_users))
    join_room('chat')
    emit_users_info(request.sid)


@socketio.on('disconnect')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user in online_users:
        try:
            online_users.remove(current_user)
            del user_to_sid[current_user.username]
            del sid_to_user[request.sid]
            logger.info("%s is disconnected." % current_user.username)
            logger.info("online users: {}".format(online_users))
        except Exception as e:
            logger.error(e)

    leave_room('chat')
    emit_users_info(request.sid)


@socketio.on('new message')
def new_message(message_body):
    message = Message(author=current_user._get_current_object(), body=message_body['body'],
                      room_name=message_body['room_name'], timestamp=datetime.utcnow())
    db.session.add(message)
    db.session.commit()

    # send to sender it self
    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message, mode=0, flag=0),
          'message_body': message_body,
          'room_name': message_body['room_name'],
          'gravatar': current_user.gravatar,
          'username': current_user.username,
          'user_id': current_user.id})
    # send to other one

    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message, mode=0, flag=1),
          'message_body': message_body,
          'room_name': message_body['room_name'],
          'gravatar': current_user.gravatar,
          'username': current_user.username,
          'user_id': current_user.id},
         to=message_body['room_name'], skip_sid=request.sid)


@socketio.on('join room')
def join(room_name):
    join_room(room_name)
    emit('joined_room', {'room_name': room_name, 'user_name': current_user.username})
    emit_users_info(request.sid)


@socketio.on('webrtc connect')
def webrtc_connect(data):
    logger.info("webrtc Connected, sid: {}".format(request.sid))
    emit('webrtc ready', room=data['room_name'], skip_sid=request.sid)


@socketio.on('webrtc data')
def webrtc_data(data):
    logger.info('Message from {}: {}'.format(request.sid, data))
    emit('webrtc data', data["data"], room=data["room_name"], skip_sid=request.sid)


def emit_users_info(sid):
    r = rooms(sid=sid)
    logger.info("{} now is in: {}".format(current_user.username, r))
    emit('users info',
         {'amount': len(online_users),
          'users': render_template('chat/_users.html', users=online_users),
          'rooms_amount': len(r),
          'rooms': render_template('chat/_rooms.html', rooms=r)})


def getUserFromUsername(username):
    flag = 0
    user = User()
    for u in online_users:
        if u.username == username:
            flag = 1
            user = u
            break
    if flag == 1:
        return user
    else:
        return None
