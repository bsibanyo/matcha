from app.all.utils import *

from app import home, profile, users, realtime

app.register_blueprint(home.bluPrint)
app.register_blueprint(users.bluPrint)
app.register_blueprint(profile.bluPrint)


def init_base():
    with app.app_context():
        interests = [
            'Music', 'Sports', 
            'Blogging', 'Movies', 
            'Art', 'Gaming', 
            'Traveling', 'Herbalism', 
            'Baking','Pets', 
            'Family','Cooking', 
            'Reading', 'Cleaning', 
            'Karaoke', 'Puzzles', 
            'Winemaking', 'Hunting'
        ]
        m_photos = "https://qph.fs.quoracdn.net/main-qimg-3ab85f7058b44486ffa67a96e2929c49.webp, https://image.shutterstock.com/image-vector/closeup-young-handsome-man-face-260nw-334298948.jpg, https://i.pinimg.com/originals/af/ac/94/afac9473e2a51a529c67fb059e38dd64.jpg, https://data.whicdn.com/images/97342183/original.jpg, https://burrow.hogwartsishere.com/media/profile_photos/a906475274daaf35b89f0d5136d23ecd--aoharu-x-machinegun-anime-animals_1.jpg, https://s3.amazonaws.com/thatsisterimages/wp-content/uploads/2019/12/12200335/Bob-Makihara-from-Tenjhe-Tenge.jpg"
        f_photos = "https://image.shutterstock.com/image-vector/face-expression-woman-smiling-female-260nw-753503635.jpg, https://i.pinimg.com/736x/11/56/24/11562429d6c4660452d9881a5cb3e104.jpg, https://i.pinimg.com/originals/bb/ea/3c/bbea3c0594964b93f4101dfe08e4b34c.jpg, https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQbb6rtIE3IRQ0vj2DZk6cHwmw_Intawtl-4OteVeYxnxUQ3mg0g&s, https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTo-W4Bl5H9RT14W8-AFDki3w1grf5GY7IVzEc0C-ShJR40Ori9lQ&s, https://i.pinimg.com/originals/46/4b/fd/464bfd68e42349148752d8b9888f72c8.jpg"
        m_photos_list = m_photos.split(',')
        f_photos_list = f_photos.split(',')
        User().create(
            username="Jack",
            gender="m",
            firstname="Mazwi".capitalize(),
            lastname="Bubblegum".capitalize(),
            birthdate="1990-09-07",
            age=calculate_age("1990-09-07"),
            email="mazwi@gmail.com",
            password=hash_pw("matchme"),
            confirm=1,
            photos=m_photos,
            main_photo=m_photos_list[randrange(0, 5)],
            latitude='-26.205171',
            longitude='28.049815',
            city='Johannesburg'.capitalize(),
            tags=','.join(sample(interests, randrange(1, 6)))
        )
        User().create(
            username="Minnie",
            gender="f",
            firstname="Minnie".capitalize(),
            lastname="May".capitalize(),
            birthdate="1985-12-15",
            age=calculate_age("1985-12-15"),
            email="minnie101@yahoo.com",
            password=hash_pw("minnie101"),
            confirm=1,
            photos=f_photos,
            main_photo=f_photos_list[randrange(0, 6)],
            latitude='-29.857896',
            longitude='31.029198',
            city='Durban'.capitalize(),
            tags=','.join(sample(interests, randrange(1, 6)))
        )
        print("Automatic accounts has been created!\n")
        for tag in interests:
            Tags().create(text=tag)
        print("Tags have been created\n")
        print("Creating Users\n")
        print("Please wait this may take a while...\n")
        populate(500, m_photos, f_photos, interests)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
        init_base()
    realtime.socketio.run(app, host='127.0.0.1', port=8080)