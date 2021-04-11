from flask import Blueprint, session, redirect, url_for, render_template, request, current_app
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from app.extends import socketio, db
from app.forms import RoomForm
from app.models import Message, Room

chat_bp = Blueprint('chat', __name__)
online_users = []


@chat_bp.route('/select_room', methods=['GET', 'POST'])
def select_room():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        form = RoomForm()
        if form.validate_on_submit():
            session['name'] = current_user.username
            session['room'] = form.room.data
            return redirect(url_for('.chat'))
        elif request.method == 'GET':
            form.room.data = session.get('room', '')
        return render_template('chat/_join_room.html', form=form)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    if request.method != 'GET':
        pass
    else:
        chat_type = request.args.get('type', 'room')  # room or user
        room_name = request.args.get('rname', 'chat')
        user_id = request.args.get('uid')
        if chat_type == 'room':
            if room_name is not None:
                # action for room
                pass
            else:
                pass
        else:
            if user_id is not None:
                # action for user
                pass
            else:
                pass


@chat_bp.route('/')
def home():
    global online_rooms

    form = RoomForm()
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name='chat').order_by(Message.timestamp.asc())[-amount:]

    return render_template('home.html', messages=messages, form=form)


@chat_bp.route('/chatroom/<room_name>',methods=['GET'])
def room_message(room_name):
    amount = current_app.config['MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(in_room=1, room_name=room_name).order_by(Message.timestamp.asc())[-amount:]
    return render_template('chat/_messages.html', messages=messages)


@socketio.on('connect')
def connect():
    global online_users
    if current_user.is_authenticated and current_user not in online_users:
        online_users.append(current_user)
    join_room('chat')
    emit('users info', {'count': len(online_users), 'users': render_template('chat/_users.html', users=online_users)},
         broadcast=True)


@socketio.on('disconnect')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user in online_users:
        online_users.remove(current_user)
    emit('users info', {'count': len(online_users), 'users': render_template('chat/_users.html', users=online_users)},
         broadcast=True)


@socketio.on('new message')
def new_message(message_body):
    message = Message(author=current_user._get_current_object(), body=message_body['body'],room_name=message_body['room_name'])
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
