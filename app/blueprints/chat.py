from datetime import datetime

from flask import Blueprint, session, redirect, url_for, render_template, request, current_app
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from app.extends import socketio
from app.forms import RoomForm
from app.models import User

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/', methods=['GET', 'POST'])
def index():
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
        return render_template('select_room.html', form=form)


@chat_bp.route('/chat')
def chat():
    # TODO 第一次登陆后不能直接进入聊天室，需要刷新一次
    """Chat room. The user's name and room must be stored in
    the session."""
    name = current_user.username
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('chat.index'))
    return render_template('chatroom.html', name=name, room=room)

@chat_bp.route('/layout')
def layout():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FRIENDS_PER_PAGE']
    pagination = User.query.order_by(User.id.desc()).paginate(1, per_page=1)
    onlion = pagination.items
    return render_template('base_client.html',pagination=pagination,onlion=onlion)



@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message',
         {'msg': '[' + datetime.now().strftime('%m-%d %H:%M') + '] ' + session.get('name') + ' : ' + message['msg']},
         room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)
