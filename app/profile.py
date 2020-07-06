from .all.forms import *
from .all.decorators import *

bluPrint = Blueprint('profile', __name__, url_prefix='/')


@bluPrint.route("profile/<username>")
@is_extended
def profile(username):
    user = User().get(username=username)
    if user.username == session['user']['username']:
        return redirect(url_for("profile.account"))
    blocks = Blocks().filter(blocker_id=user.id, blocked_id=session['user']['id']) + Blocks().filter(blocked_id=user.id, blocker_id=session['user']['id'])
    if len(blocks) > 0:
        user.__dict__ = {}
    if user.exists():
        report = Reports().get(from_id=session['user']['id'], dest_id=user.id)
        if not report.exists():
            report = None
        if type(user.photos) is not list and user.photos:
            user.photos = user.photos.split(',')
        if type(user.orientation) is not list and user.orientation:
            user.orientation = user.orientation.split(",")
        if type(user.tags) is not list and user.tags:
            user.tags = user.tags.split(",")
        if user.last_connection:
            user.last_connection = parser.parse(user.last_connection).strftime("%d-%m-%Y")
        like = Likes().get(from_id=session['user']['id'], dest_id=user.id)
        if not like.exists():
            like = Likes().get(dest_id=session['user']['id'], from_id=user.id)
            if not like.exists():
                like = None
        distance = get_distance((user.latitude, user.longitude), (session['user']['latitude'], session['user']['longitude']))
        return render_template("profile.html", **locals())
    else:
        session['message'] = "profile not found"
        return redirect(url_for("home.home"))


@bluPrint.route("/inbox")
@is_extended
def inbox():
    chats = Chats().filter(from_id=session['user']['id']) + Chats().filter(dest_id=session['user']['id'])
    chats.sort(key=lambda x: x.date, reverse=True)
    return render_template("inbox.html", **locals())


@bluPrint.route("/inbox/<conv_id>", methods=['GET'])
@is_extended
def get_conv(conv_id):
    form = MessageForm()
    conv = Chats().get(id=conv_id)
    my_id = session['user']['id']
    if conv.dest_id != my_id and conv.from_id != my_id:
        session['message'] = "Conversation not found"
        return redirect(url_for("home.home"))
    if conv.dest_id == my_id:
        conv.update('id', conv.id, dest_unread=0)
    elif conv.from_id == my_id:
        conv.update('id', conv.id, from_unread=0)
    messages = conv.content.split('\r\n')
    messages = reversed(messages)
    return render_template("conv.html", **locals())


@bluPrint.route("/notifs")
@is_extended
def notifs():
    typ = request.args.get('type', None, str)
    my_id = session['user']['id']
    if not typ:
        dis_notifs = Notifs().filter(dest_id=my_id, unread=1)
        dis_notifs.sort(key=lambda x: x.id, reverse=True)
        Notifs().update('dest_id', session['user']['id'], unread=0)
        return render_template("notifs.html", **locals())
    likes = Likes().filter(from_id=my_id) + Likes().filter(dest_id=my_id)
    likes.sort(key=lambda x: x.id, reverse=True)
    matched = set()
    liked = set()
    for like in likes:
        if like.returned:
            matched.add(like.dest_id if like.from_id == my_id else like.from_id)
        else:
            liked.add(like.dest_id if like.from_id == my_id else like.from_id)
    matched = list(matched)
    liked = list(liked)
    all_users = User().all()
    if typ == 'matchs':
        matchers = list()
        for user in all_users:
            if user.id in matched:
                matchers.insert(matched.index(user.id), user.username)
        return render_template("notifs.html", **locals())
    if typ == 'likes':
        likers = list()
        for user in all_users:
            if user.id in liked:
                likers.insert(liked.index(user.id), user.username)
        return render_template("notifs.html", **locals())


@bluPrint.route("account")
@is_authenticated
def account():
    message = session.pop("message", None)
    user = session['user']
    if not user['latitude'] or not user['longitude'] or not user['city'] or user['city'] == 'None':
        ip_info = get_ip_info(request.remote_addr)
        User().update('id', user['id'], latitude=ip_info['latitude'], longitude=ip_info['longitude'], city=ip_info['city'])
        session['user'] = User().get(id=session['user']['id']).__dict__
    if type(user['photos']) is not list and user['photos']:
        user['photos'] = user['photos'].split(',')
    if type(user['orientation']) is not list and user['orientation']:
        user['orientation'] = user['orientation'].split(",")
    if type(user['tags']) is not list and user['tags']:
        user['tags'] = user['tags'].split(",")
    return render_template("account.html", **locals())


@bluPrint.route("account/edit", methods=['GET', 'POST'])
@is_authenticated
def edit_account():
    session['user'] = User().get(id=session['user']['id']).__dict__
    message = session.pop("message", None)
    user = session['user']
    tags = Tags().all(only='text')
    tags_hidden = ','.join(tags)
    form = profileForm()
    if type(user['photos']) is not list and user['photos']:
        user['photos'] = user['photos'].split(',')
    if type(user['orientation']) is not list and user['orientation']:
        user['orientation'] = user['orientation'].split(',')
    if type(user['tags']) is not list and user['tags']:
        user['tags'] = user['tags'].split(',')
    if user['bio']:
        user['bio'] = unescape(user['bio'].replace('<br>', '\n'))
    if request.method == "GET":
        return render_template("edit.html", **locals())
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if len(errors) > 0:
            return render_template("edit.html", **locals())
        bio = escape(post['bio'], quote=True).strip().split('\n')
        bio_rendering = []
        bio_len = len(bio)
        for i, line in enumerate(bio):
            if i not in (0, bio_len):
                bio_rendering.append('<br>' + line)
            else:
                bio_rendering.append(line)
        bio_rendering = ''.join(bio_rendering)
        User().update('id', session['user']['id'], gender=post['gender'], orientation=','.join(post.getlist('orientation')), bio=bio_rendering)
        session['message'] = "profile update!"
        return redirect(url_for("profile.account"))


@bluPrint.route("account/edit/photos/add", methods=['POST'])
@is_authenticated
def add_photos():
    photos = session['user']['photos'] or list()
    if type(photos) is not list:
        photos = photos.split(",")
    if len(photos) < 5:
        photo = request.form['photo']
        if re.search("^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$", photo):
            photos.append(photo)
            photos = ",".join(photos)
            User().update('id', session['user']['id'], photos=photos)
            return redirect(url_for("profile.edit_account"))
        else:
            session['message'] = "Photo url does not appear to be valid."
    else:
        session['message'] = "The number of photos is limited to 5 per user."
    return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/photos/delete", methods=['GET'])
@is_authenticated
def delete_photo():
    photos = session['user']['photos'] or list()
    if type(photos) is not list:
        photos = photos.split(",")
    for i, j in enumerate(photos):
        if i == int(request.args.get('id')):
            photos.remove(j)
            photos = ",".join(photos)
            User().update('id', session['user']['id'], photos=photos)
    return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/photos/define", methods=['GET'])
@is_authenticated
def define_main_photo():
    photos = session['user']['photos'] or list()
    if type(photos) is not list:
        photos = photos.split(",")
    for i, j in enumerate(photos):
        if i == int(request.args.get('id')):
            User().update('id', session['user']['id'], main_photo=j)
    return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/geolocation", methods=['POST'])
@is_authenticated
def define_geolocation():
    addr = request.form['addr']
    lat, lng, city = get_coordinates_from_addr(addr)
    User().update('id', session['user']['id'], latitude=lat, longitude=lng, city=city)
    return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/password", methods=['GET', 'POST'])
@is_authenticated
def reset_password():
    form = NewPasswordForm()
    if request.method == "GET":
        return render_template("reset-done.html", form=form)
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if post['pwd'] and post['cpwd'] and post['pwd'] != post['cpwd']:
            errors.append("Passwords are not the same.")
        if len(errors) > 0:
            return render_template("reset-done.html", **locals())
        User().update('id', session['user']['id'], password=hash_pw(post['pwd']))
        session['message'] = "Password has been changed!"
        return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/tags/add", methods=['POST'])
def add_tags():
    tags = session['user']['tags'] or list()
    if type(tags) is not list:
        tags = tags.split(",")
    if len(tags) < 5:
        tag = escape(request.form['tag'])
        if tag not in tags:
            tags.append(tag.capitalize())
            User().update('id', session['user']['id'], tags=','.join(tags))
        tags = Tags().all(only='text')
        if tag not in tags:
            Tags().create(text=tag)
    else:
        session['message'] = "Tags must be 5 per user"
    return redirect(url_for("profile.edit_account"))


@bluPrint.route("account/edit/tags/delete", methods=['GET'])
def delete_tags():
    tags = session['user']['tags'] or list()
    if type(tags) is not list:
        tags = tags.split(",")
    tag = escape(str(request.args.get('tag')))
    taggs = copy(tags)
    tags.remove(tag)
    if tags != taggs:
        User().update('id', session['user']['id'], tags=','.join(tags))
    return redirect(url_for("profile.edit_account"))
