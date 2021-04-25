from datetime import datetime

from flask import Blueprint, render_template, current_app, request
from flask_login import current_user
from flask_socketio import emit, join_room, rooms, leave_room

from app.extends import socketio, db
from app.forms import RoomForm
from app.models import Message, User

chat_bp = Blueprint('chat', __name__)
online_users = []
user_to_sid = {}  # 映射username to session.id
sid_to_user = {}


@chat_bp.route('/')
def home():
    global online_rooms

    form = RoomForm()
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name='chat').order_by(Message.timestamp.asc())[-amount:]

    return render_template('home.html', messages=messages, form=form, mode=1)


# AJAX message interface
@chat_bp.route('/chatroom/<room_name>', methods=['GET'])
def room_message(room_name):
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name=room_name).order_by(Message.timestamp.asc())[-amount:]
    return render_template('chat/_messages.html', messages=messages)


# experimental p2p chat
@chat_bp.route('/p/<username>')
def private_chat(username):
    # return redirect('http://127.0.0.1/p/' + uuid)
    sid = user_to_sid[username]
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
    if current_user.is_authenticated and current_user not in online_users:
        emit("username", current_user.username)
        online_users.append(current_user)
        print(online_users)
        user_to_sid[current_user.username] = request.sid
        sid_to_user[request.sid] = current_user.username
        print("%s is connected." % current_user.username)

    join_room('chat')
    emit_users_info(request.sid)


@socketio.on('disconnect')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user in online_users:
        print("del user: ", current_user)
        online_users.remove(current_user)
        print(online_users)
        del user_to_sid[current_user.username]
        del sid_to_user[request.sid]
        print("%s is disconnected." % current_user.username)
    leave_room('chat')
    emit_users_info(request.sid)


@socketio.on('new message')
def new_message(message_body):
    message = Message(author=current_user._get_current_object(), body=message_body['body'],
                      room_name=message_body['room_name'], timestamp=datetime.utcnow())

    print(render_template('chat/_message.html', message=message, mode=0, self=1))
    print(current_user)
    print(message.author)
    print(render_template('chat/_message.html', message=message, mode=0, self=0))

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
    print("webrtc Connected ", request.sid)
    emit('webrtc ready', room=data['room_name'], skip_sid=request.sid)


@socketio.on('webrtc data')
def webrtc_data(data):
    print('Message from {}: {}'.format(request.sid, data))
    emit('webrtc data', data["data"], room=data["room_name"], skip_sid=request.sid)


def emit_users_info(sid):
    global online_users
    r = rooms(sid=sid)
    print(current_user.username + " now is in: ", end="")
    print(r)
    emit('users info',
         {'amount': len(online_users),
          'users': render_template('chat/_users.html', users=online_users),
          'rooms_amount': len(r),
          'rooms': render_template('chat/_rooms.html', rooms=r)})


def getUserFromUsername(username):
    global online_users
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
