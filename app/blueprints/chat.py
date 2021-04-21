from flask import Blueprint, redirect, render_template, current_app
from flask_login import current_user
from flask_socketio import emit, join_room, rooms, leave_room

from app.extends import socketio, db
from app.forms import RoomForm
from app.models import Message

chat_bp = Blueprint('chat', __name__)
online_users = []


@chat_bp.route('/')
def home():
    global online_rooms

    form = RoomForm()
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name='chat').order_by(Message.timestamp.asc())[-amount:]

    return render_template('home.html', messages=messages, form=form)


# AJAX message interface
@chat_bp.route('/chatroom/<room_name>', methods=['GET'])
def room_message(room_name):
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name=room_name).order_by(Message.timestamp.asc())[-amount:]
    return render_template('chat/_messages.html', messages=messages)


# experimental p2p chat
@chat_bp.route('/p/<uuid>')
def chat_url(uuid):
    return redirect('http://127.0.0.1/p/' + uuid)


@socketio.on('connect')
def connect():
    global online_users
    if current_user.is_authenticated and current_user not in online_users:
        online_users.append(current_user)
        print("%s is connected." % current_user.username)

    join_room('chat')
    r = rooms()
    emit('users info',
         {'amount': len(online_users),
          'users': render_template('chat/_users.html', users=online_users),
          'rooms_amount': len(r),
          'rooms': render_template('chat/_rooms.html', rooms=r)},
         broadcast=True)


@socketio.on('disconnect')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user in online_users:
        online_users.remove(current_user)
        print("%s is disconnected." % current_user.username)
    leave_room('chat')
    emit('users info',
         {'all_amount': len(online_users), 'all_users': render_template('chat/_users.html', users=online_users)},
         broadcast=True)


@socketio.on('new message')
def new_message(message_body):
    message = Message(author=current_user._get_current_object(), body=message_body['body'],
                      room_name=message_body['room_name'])
    db.session.add(message)
    db.session.commit()
    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message),
          'message_body': message_body,
          'gravatar': current_user.gravatar,
          'username': current_user.username,
          'user_id': current_user.id},
         broadcast=True)


@socketio.on('join room')
def join(room_name):
    join_room(room_name.lower())
    emit('joined_room', {'room_name': room_name, 'user_name': current_user.username})
    r = rooms()
    emit('users info',
         {'amount': len(online_users),
          'users': render_template('chat/_users.html', users=online_users),
          'rooms_amount': len(r),
          'rooms': render_template('chat/_rooms.html', rooms=r)},
         broadcast=True)
