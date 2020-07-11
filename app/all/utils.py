from . import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import math
from opencage.geocoder import OpenCageGeocode
from requests import get
from random import randrange, sample, shuffle

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = PROJECT_DIR + '/matcha.db'

app = Flask("Matcha", template_folder="app/templates", static_folder="app/static")
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "M@tch@"
app.config['WTF_CSRF_ENABLED'] = True
GMAIL_CRED = ("matchawithai@gmail.com", "@Bcd1234")

opencagedata_key = "e118fe302e244090803c07bd74de2a5b"
ipstack_key = "a69f40747fc519afa2b2b764e64e270c"

csrf = CSRFProtect()
csrf.init_app(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def profile_extended(user):
    user = User().init(**user)
    if not user.bio or not user.orientation or not user.tags or not user.photos or not user.main_photo:
        return False
    return True


def populate(num, m_photos, f_photos, interests):
    with app.app_context():
        coordinates = list()
        if os.path.exists(PROJECT_DIR + '/coordinates.txt'):
            with open(PROJECT_DIR + '/coordinates.txt') as f:
                for line in f.readlines():
                    l = line.split(",")
                    if len(l) > 0:
                        coordinates.append((l[1], l[3]))
        else:
            exit(1)
        m_photos_list = m_photos.split(',')
        f_photos_list = f_photos.split(',')
        peoples = get('https://randomuser.me/api/?results={}&nat=US'.format(num)).json()['results']
        for i, people in enumerate(peoples):
            if people['gender'] == 'male':
                User().create(
                    username=people['login']['username'],
                    gender="m",
                    firstname=people['name']['first'].capitalize(),
                    lastname=people['name']['last'].capitalize(),
                    birthdate=people['dob']['date'],
                    age=people['dob']['age'],
                    email=people['email'],
                    password=hash_pw(people['login']['password']),
                    confirm=1,
                    photos=m_photos,
                    main_photo=m_photos_list[randrange(0, 5)],
                    latitude=coordinates[i][0],
                    longitude=coordinates[i][1],
                    city=people['location']['city'].capitalize(),
                    tags=','.join(sample(interests, randrange(1, 6)))
                )
            else:
                User().create(
                    username=people['login']['username'],
                    gender="f",
                    firstname=people['name']['first'].capitalize(),
                    lastname=people['name']['last'].capitalize(),
                    birthdate=people['dob']['date'],
                    age=people['dob']['age'],
                    email=people['email'],
                    password=hash_pw(people['login']['password']),
                    confirm=1,
                    photos=f_photos,
                    main_photo=f_photos_list[randrange(0, 5)],
                    latitude=coordinates[i][0],
                    longitude=coordinates[i][1],
                    city=people['location']['city'].capitalize(),
                    tags=','.join(sample(interests, randrange(1, 6)))
                )


@app.teardown_appcontext
def close_connection(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with open('{}/matcha.sql'.format(PROJECT_DIR), 'r') as f:
            cur.executescript(f.read())
    print("Database has been successfully created.\n")


def hash_pw(pw):
    return sha3_512(pw.encode("utf-8")).hexdigest()


def gener_token(size=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def send_mail(dest, subject, message):
    mail = MIMEMultipart()
    mail['From'] = GMAIL_CRED[0]
    mail['To'] = dest
    mail['Subject'] = subject
    mail.attach(MIMEText(message))

    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.ehlo()
    s.login(GMAIL_CRED[0], GMAIL_CRED[1])
    s.sendmail(GMAIL_CRED[0], dest, mail.as_string())
    s.close()


def calculate_age(birthdate):
    today = datetime.date.today()
    bd = list(map(int, birthdate.split("-")))
    return today.year - bd[0] - ((today.month, today.day) < (bd[1], bd[2]))


def get_ip_info(ip):
    if ip in ('127.0.0.1', 'localhost'):
        ip = "185.15.27.37"
    info = get("http://api.ipstack.com/{}?access_key={}&format=1".format(ip, ipstack_key)).json()
    return info


def get_coordinates_from_addr(addr):
    geocoder = OpenCageGeocode(opencagedata_key)
    results = geocoder.geocode(addr)
    return results[0]['geometry']['lng'], results[0]['geometry']['lat'], results[0]['components']['city']


def get_distance(coord1, coord2):
    R = 6373
    lat1, lon1 = float(coord1[0]), float(coord1[1])
    lat2, lon2 = float(coord2[0]), float(coord2[1])

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def same_tags(p1, p2):
    tp1 = p1.split(',') if type(p1) is not list else p1
    tp2 = p2.split(',') if type(p2) is not list else p2
    count = 0
    for i in tp1:
        if i in tp2:
            count += 1
    return count


@app.context_processor
def inject_conv():
    if 'user' in session.keys():
        session['user'] = User().get(id=session['user']['id']).__dict__
        session['user']['is_extended'] = profile_extended(session['user'])
        id = session['user']['id']
        conv = Chats().all()
        convs = []
        for c in conv:
            if c.dest_id == id and c.dest_unread:
                convs.append(c)
            if c.from_id == id and c.from_unread:
                convs.append(c)
        notifs = Notifs().filter(dest_id=id, unread=1)
        notifs.sort(key=lambda x: x.id, reverse=True)
        return dict(convs=convs, notifs=notifs)
    return {}
