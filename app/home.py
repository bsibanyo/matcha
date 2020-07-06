from .all.forms import *
from .all.decorators import *
from numpy import average

bluPrint = Blueprint('home', __name__, url_prefix='/')


@bluPrint.route("/", methods=['GET', 'POST'])
@is_authenticated
def home():
    form = FilterSearchForm()
    message = session.pop("message", None)
    users = User().all()
    my_lat = session['user']['latitude']
    my_lng = session['user']['longitude']
    gender = session['user']['gender']
    tags = session['user']['tags']
    pop = session['user']['popularity']
    orientation = session['user']['orientation']
    my_id = session['user']['id']
    why_not = []
    if request.method == 'GET':
        for user in users:
            user.orientation = user.orientation.split(',')
            if gender not in user.orientation or user.gender not in orientation or user.id == my_id:
                continue
            if user.last_connection:
                user.last_connection = parser.parse(user.last_connection).strftime("%d-%m-%Y")
            user.distance = get_distance((my_lat, my_lng), (user.latitude, user.longitude))
            distance = max(0, 100 - user.distance)
            user.s_tags = same_tags(tags, user.tags)
            popularity = 100 * (max(0.1, min(pop, user.popularity)) / max([0.1, pop, user.popularity]))
            av = average([distance, user.s_tags, popularity], weights=[2, 3, 1])
            if av >= 15:
                why_not.append(user)
        shuffle(why_not)
        w_copy = copy(why_not)
        for u in w_copy:
            blocks = Blocks().filter(blocker_id=u.id, blocked_id=my_id) + Blocks().filter(blocked_id=u.id, blocker_id=my_id)
            if len(blocks) > 0:
                why_not.remove(u)
        why_not = why_not[:12]
        return render_template("home.html", **locals())
    else:
        post = request.form
        errors = form.validate(**post)
        for user in users:
            user.orientation = user.orientation.split(',')
            if gender not in user.orientation or user.gender not in orientation or user.id == my_id:
                continue
            if (post['min_age'] and int(user.age) < int(post['min_age'])) or (post['max_age'] and int(user.age) > int(post['max_age'])):
                continue
            if (post['min_pop'] and float(user.popularity) < float(post['min_pop'])) or (post['max_pop'] and float(user.popularity) > float(post['max_pop'])):
                continue
            user.distance = get_distance((my_lat, my_lng), (user.latitude, user.longitude))
            if post['distance'] and user.distance > float(post['distance']):
                continue
            if type(user.tags) is str:
                user.tags = user.tags.split(',')
            tags = list(map(lambda x: x.strip().capitalize(), post['tags'].split(',')))
            user.s_tags = sum(t in tags for t in user.tags)
            if post['tags']:
                if user.s_tags == 0:
                    continue
            if user.last_connection:
                user.last_connection = parser.parse(user.last_connection).strftime("%d-%m-%Y")
            why_not.append(user)
        w_copy = copy(why_not)
        for u in w_copy:
            blocks = Blocks().filter(blocker_id=u.id, blocked_id=my_id) + Blocks().filter(blocked_id=u.id, blocker_id=my_id)
            if len(blocks) > 0:
                why_not.remove(u)
        if post['sort'] and post['sort'] == 's_tags':
            why_not.sort(key=lambda x: getattr(x, post['sort']), reverse=True)
        elif post['sort']:
            why_not.sort(key=lambda x: getattr(x, post['sort']))
        else:
            shuffle(why_not)
        return render_template("home.html", **locals())
