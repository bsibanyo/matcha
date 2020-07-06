from app.all import *
from .all.decorators import *
from .all.models import *

socketio = SocketIO(app)


@socketio.on('connect')
@is_authenticated
def connect():
    try:
        User().update('id', session['user']['id'], socket=request.sid, is_connected=1)
    except:
        pass


@socketio.on('disconnect')
def disconnect():
    try:
        User().update('id', session['user']['id'], socket='', is_connected=0)
    except:
        pass


@is_authenticated
@socketio.on('new message')
def new_message(json):
    dest = User().get(id=json['dest_id'])
    conv = Chats().get(from_id=session['user']['id'], dest_id=json['dest_id'])
    json['content'] = escape(json['content'], quote=True)
    if conv.exists():
        content = conv.content + "\r\n{}".format(json['content'])
        Chats().update('id', conv.id, content=content, dest_unread=1, from_unread=1)
    else:
        conv = Chats().get(dest_id=session['user']['id'], from_id=json['dest_id'])
        if conv.exists():
            content = conv.content + "\r\n{}".format(json['content'])
            Chats().update('id', conv.id, content=content, dest_unread=1, from_unread=1)
        else:
            conv = Chats().create(from_id=session['user']['id'], dest_id=json['dest_id'], content=json['content'], dest_unread=1)
    link = url_for("profile.get_conv", conv_id=conv.id)
    if dest.socket:
        emit('new notif', {'message': 'New message !', 'link': link}, room=dest.socket)
    else:
        Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='message')


@is_authenticated
@socketio.on('new visit')
def new_visit(json):
    visitor = User().get(id=json['from_id'])
    dest = User().get(id=json['dest_id'])
    visit = Visits().get(from_id=json['from_id'], dest_id=json['dest_id'])
    link = url_for("profile.profile", username=visitor.username)
    if visit.exists():
        now = datetime.datetime.now()
        diff = now - parser.parse(visit.date)
        visit.update('id', visit.id, date=datetime.datetime.now())
        if diff.total_seconds() >= 300:
            if dest.socket:
                emit('new notif', {'message': '{} just checked you out!'.format(visitor.username), 'link': link}, room=dest.socket)
            else:
                Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='visit')
    else:
        Visits().create(from_id=json['from_id'], dest_id=json['dest_id'])
        if dest.socket:
            emit('new notif', {'message': '{} just checked you out!'.format(visitor.username), 'link': link}, room=dest.socket)
        else:
            Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='visit')


@is_authenticated
@socketio.on('new like')
def new_like(json):
    liker = User().get(id=json['from_id'])
    dest = User().get(id=json['dest_id'])
    dest.update('id', dest.id, popularity=dest.popularity + 0.25)
    like = Likes().get(from_id=json['from_id'], dest_id=json['dest_id'])
    link = url_for("profile.profile", username=liker.username)
    if not like.exists():
        like = Likes().get(dest_id=json['from_id'], from_id=json['dest_id'])
        if like.exists():
            if not like.returned:
                like.update('id', like.id, returned=1)
                if dest.socket:
                    emit('new notif', {'message': 'You match with {} !'.format(liker.username), 'link': link},
                         room=dest.socket)
                else:
                    Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='like')
        else:
            Likes().create(from_id=liker.id, dest_id=dest.id)
            if dest.socket:
                emit('new notif', {'message': 'Looks like {}, likes your profile!'.format(liker.username), 'link': link},
                     room=dest.socket)
            else:
                Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='like')


@is_authenticated
@socketio.on('unlike')
def unlike(json):
    liker = User().get(id=json['from_id'])
    dest = User().get(id=json['dest_id'])
    dest.update('id', dest.id, popularity=dest.popularity - 0.25)
    like = Likes().get(from_id=json['from_id'], dest_id=json['dest_id'])
    link = url_for("profile.profile", username=liker.username)
    if like.exists():
        if like.returned:
            like.update('id', like.id, from_id=like.dest_id, dest_id=like.from_id, returned=0)
        else:
            like.delete('id', like.id)
        if dest.socket:
            emit('new notif', {'message': 'Oops, {} just unliked your profile!'.format(liker.username), 'link': link},
                 room=dest.socket)
        else:
            Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='unlike')
    else:
        like = Likes().get(dest_id=json['from_id'], from_id=json['dest_id'])
        if like.exists():
            like.update('id', like.id, returned=0)
            if dest.socket:
                emit('new notif', {'message': 'Oops, {} just unliked your profile!'.format(liker.username), 'link': link},
                     room=dest.socket)
            else:
                Notifs().create(from_username=session['user']['username'], dest_id=dest.id, type='unlike')


@socketio.on('report')
def report(json):
    report = Reports().get(from_id=json['from_id'], dest_id=json['dest_id'])
    if not report.exists():
        Reports().create(from_id=json['from_id'], dest_id=json['dest_id'])


@socketio.on('block')
def block(json):
    blocks = Blocks().filter(blocker_id=json['from_id'], blocked_id=json['dest_id']) + Blocks().filter(blocked_id=json['dest_id'], blocker_id=json['from_id'])
    if len(blocks) == 0:
        Blocks().create(blocker_id=json['from_id'], blocked_id=json['dest_id'])
