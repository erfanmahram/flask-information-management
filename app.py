import datetime
import sqlite3
import os
from flask import Flask, render_template, request, url_for, flash, redirect, abort, send_file, jsonify
from flask_login import UserMixin, login_required, logout_user, current_user, login_user, LoginManager
from http import HTTPStatus
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
import db_config
import hashlib
from models import Files
from logzero import logger
import logzero

logzero.logfile("./logs/rotating-logfile.log", maxBytes=1000000, backupCount=10)

app = Flask(__name__, static_folder='static', static_url_path='/static/')

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "1234"
app.config["SQLALCHEMY_DATABASE_URI"] = db_config.connection_string
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

name_dict = {'ردیف(Id)': 'Id', 'نام نماینده': 'AgentName', 'شماره تلفن نماینده': 'AgentPhone', 'مساحت واحد': 'UnitArea',
             'مساحت زمین': 'TotalArea', 'سونا خشک': 'DrySauna', 'امکان پذیرش معلولین': 'DisabledReception',
             'تلویزیون': 'TV', 'گیرنده دیجیتال': 'DigitalReciever', 'یخچال': 'Refrigerator', 'اجاق گاز': 'Oven',
             'سرویس غذاخوری': 'DiningService', 'مبلمان': 'Furniture', 'جاروبرقی': 'VacuumMachine',
             'توالت ایرانی': 'PersianToilet', 'توالت فرنگی': 'Toilet', 'حمام': 'Bathroom',
             'میز و صندلی': 'DiningFurniture', 'حیاط اختصاصی': 'PrivateYard', 'آسانسور': 'Elevator',
             'کولر آبی': 'EvaporativeCooler', 'کولر گازی': 'AirConditioner', 'شوفاژ': 'Radiator', 'شومینه': 'Fireplace',
             'وای فای رایگان': 'FreeWifi', 'اتو': 'Iron', 'ماشین لباسشویی': 'WashingMachine', 'جکوزی': 'Jacuzzi',
             'مایکروویو': 'Microwave', 'باربیکیو': 'Barbecue', 'وان': 'Bathtub', 'چای ساز': 'TeaMaker',
             'بازی فکری': 'BoardGame', 'پینگ پونگ': 'PingPong', 'سیستم صوتی': 'SoundSystem', 'بیلیارد': 'Billiards',
             'فوتبال دستی': 'TableFootball', 'کنسول بازی': 'GameConsole', 'دوربین مدار بسته': 'CCTV', 'تخت خواب': 'Bed',
             'ایوان': 'Porch', 'استخر کودکان': 'KidsPool', 'حوضچه آبسرد': 'ColdWaterPool', 'ایر هاکی': 'AirHockey',
             'وان جکوزی': 'JacuzziTub', 'امکان ورود حیوانات خانگی': 'Pets', 'امکان برگزاری مراسم': 'Seremony',
             'آنتن دهی همراه اول': 'MCIAnten', 'آنتن دهی ایرانسل': 'IrancellAnten', 'اینترنت همراه اول': 'MCINet',
             'اینترنت ایرانسل': 'IrancellNet', 'نام میزبان': 'HostName', 'قیمت پیشنهادی': 'SuggestedPrice',
             'توضیحات اضافه': 'OtherDescriptions', 'عنوان': 'Title', 'تلفن': 'Phone', 'تصاویر': 'Media',
             'استان': 'Province', 'شهر': 'City', 'روستا': 'Village', 'آدرس': 'Address', 'طبقه': 'Floor',
             'پلاک': 'HouseNumber', 'کد پستی': 'PostalCode', 'نوع مالکیت': 'OwnershipType',
             'بافت محیط': 'EnvironmentType', 'مسیر دسترسی': 'AccessPath', 'توضیحات مسیر دسترسی': 'AccessDescription',
             'همسایگی': 'NeighbourhoodShip', 'فاصله از مکانها': 'DistanceToPlaces', 'نوع دیوارها': 'Walls',
             'ظرفیت': 'Capacity', 'حداکثر ظرفیت': 'MaxCapacity', 'تعداد اتاقها': 'Rooms',
             'تعداد سرویس کف خواب': 'SleepServices', 'تعداد تختخواب تک نفره': 'SingleBed',
             'تعداد تختخواب دو نفره': 'DoubleBed', 'تعداد مبل تختخواب شو': 'FoldingSofa',
             'تعداد سرویس بهداشتی': 'WCQuantity', 'امکانات بهداشتی': 'SanitaryFacilities', 'استخر': 'Pool',
             'سونا بخار': 'WetSauna', 'پارکینگ': 'Parking', 'تراس': 'Balcony',
             'امکان پذیرش سالمندان': 'EldersReception', 'امکانات اتاق پذیرایی': 'HallFacilities',
             'سیستم گرمایشی اتاق پذیرایی': 'HallHeater', 'سیستم سرمایشی اتاق پذیرایی': 'HallCooler',
             'سیستم گرمایشی اتاق ها': 'RoomHeater', 'سیستم سرمایشی اتاق ها': 'RoomCooler', 'حیاط': 'Yard',
             'باغ': 'Garden', 'امکانات باغ': 'GardenFacilities', 'توضیحات باغ': 'GardenDescription',
             'ویو اقامتگاه': 'View', 'امکانات رفاهی': 'ProsperityFacilities', 'امکانات سرگرمی': 'JoyFacilities',
             'امکاناتپخت و پز': 'CookingFacilities', 'سرو غذا و نوشیدنی': 'Dishes',
             'تعداد پله های ورودی': 'EntranceSteps', 'ساعت ورود': 'EnterHour', 'ساعت خروج': 'ExitHour',
             'حداقل مدت اقامت': 'MinStay', 'حداکثر مدت اقامت': 'MaxStay',
             'آخرین روز فعال در تقویم': 'LastCalenderAvailable', 'قوانین کنسلی': 'CancelRules',
             'مدارک مورد نیاز': 'RequiredDocuments', 'قوانین حیوانات خانگی': 'PetsRules',
             'شرایط برگزاری مراسم': 'SeremonyConditions', 'سایر قوانین': 'OtherRules', 'کد میزبان': 'HostCode',
             'تعداد کل طبقات': 'TotalFloors'}


@login_manager.unauthorized_handler
def unauthorized():
    abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for('index'))


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"ID: {self.id}, username: {self.username}"


with app.app_context():
    db.create_all()


def get_post(post_id):
    post = db.session.query(Files).filter(Files.Id == post_id).first()
    if post is None:
        abort(404)
    return post


ROWS_PER_PAGE = 10
salt = "pkh5"


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password") + salt
        user = Users(username=request.form.get("username"),
                     password=hashlib.md5(password.encode()).hexdigest())
        db.session.add(user)
        db.session.commit()
        cur_user = {'user_id': current_user.id, 'username': current_user.username}
        logger.warning(f"user {cur_user} registered")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password") + salt
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == hashlib.md5(password.encode()).hexdigest():
            login_user(user)
            cur_user = {'user_id': current_user.id, 'username': current_user.username}
            logger.warning(f"user {cur_user} logged in")
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout/")
def logout():
    cur_user = {'user_id': current_user.id, 'username': current_user.username}
    logout_user()
    logger.warning(f"user {cur_user} logged out")
    return redirect(url_for("index"))


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        page_rows = request.form.get("page-rows")
        files = name_dict[request.form.get("sort-files")]
        order = request.form.get("sort-order")
        page = request.args.get('page', 1, type=int)
        column_names = [i.name for i in Files.metadata.tables['Files'].columns._all_columns]
        posts = db.paginate(
            db.session.query(Files).order_by(getattr(Files,files).asc() if order == 'صعودی' else getattr(Files,files).desc()),
            page=page, per_page=int(page_rows))
        return render_template('index.html', posts=posts, column_names=column_names)
    elif request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        column_names = [i.name for i in Files.metadata.tables['Files'].columns._all_columns]
        posts = db.paginate(db.session.query(Files).order_by(Files.Id.asc()), page=page, per_page=10)
        return render_template('index.html', posts=posts, column_names=column_names)


@app.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        agent_name = request.form['agent-name']
        agent_phone = request.form['agent-phone']
        phone = request.form['phone']
        title = request.form['title']
        province = request.form['province']
        city = request.form['city']
        village = request.form['village']
        address = request.form['address']
        floor = request.form['floor']
        number = request.form['house-number']
        postal_code = request.form['postal-code']
        ownership_type = request.form['ownership-type']
        environment_type = request.form['environment-type']
        access_path = request.form['access-path']
        access_description = request.form['access-description']
        neighbourhoodship = request.form['neighbourhoodship']
        distance_to_places = request.form['distance-to-places']
        walls = request.form['walls']
        unit_area = request.form['unit-area']
        total_area = request.form['total-area']
        capacity = request.form['capacity']
        max_capacity = request.form['max-capacity']
        rooms = request.form['rooms']
        sleep_services = request.form['sleep-services']
        single_bed = request.form['single-bed']
        double_bed = request.form['double-bed']
        folding_sofa = request.form['folding-sofa']
        wc_number = request.form['wc']
        sanitary_facilities = request.form['sanitary-facilities']
        pool = True if request.form.get('pool') else False
        dry_sauna = True if request.form.get('dry-sauna') == "on" else False
        wet_sauna = True if request.form.get('wet-sauna') == "on" else False
        parking = True if request.form.get('parking') == "on" else False
        balcony = True if request.form.get('balcony') == "on" else False
        elders_reception = True if request.form.get('elders-reception') == "on" else False
        disabled_reception = True if request.form.get('disabled-reception') == "on" else False
        tv = True if request.form.get('tv') == "on" else False
        digital_reciever = True if request.form.get('digital-reciever') == "on" else False
        refrigerator = True if request.form.get('refrigerator') == "on" else False
        oven = True if request.form.get('oven') == "on" else False
        dining_service = True if request.form.get('dining-service') == "on" else False
        furniture = True if request.form.get('furniture') == "on" else False
        vacuum_machine = True if request.form.get('vacuum-machine') == "on" else False
        persian_toilet = True if request.form.get('persian-toilet') == "on" else False
        toilet = True if request.form.get('toilet') == "on" else False
        bathroom = True if request.form.get('bathroom') == "on" else False
        dining_furniture = True if request.form.get('dining-furniture') == "on" else False
        private_yard = True if request.form.get('private-yard') == "on" else False
        elevator = True if request.form.get('elevator') == "on" else False
        evaporative_cooler = True if request.form.get('evaporative-cooler') == "on" else False
        air_conditioner = True if request.form.get('air-conditioner') == "on" else False
        radiator = True if request.form.get('radiator') == "on" else False
        fireplace = True if request.form.get('fireplace') == "on" else False
        freewifi = True if request.form.get('freewifi') == "on" else False
        iron = True if request.form.get('iron') == "on" else False
        washing_machine = True if request.form.get('washing-machine') == "on" else False
        jacuzzi = True if request.form.get('jacuzzi') == "on" else False
        microwave = True if request.form.get('microwave') == "on" else False
        barbecue = True if request.form.get('barbecue') == "on" else False
        bathtub = True if request.form.get('bathtub') == "on" else False
        tea_maker = True if request.form.get('tea-maker') == "on" else False
        boardgame = True if request.form.get('boardgame') == "on" else False
        pingpong = True if request.form.get('pingpong') == "on" else False
        sound_system = True if request.form.get('sound-system') == "on" else False
        billiards = True if request.form.get('billiards') == "on" else False
        table_football = True if request.form.get('table-football') == "on" else False
        game_console = True if request.form.get('game-console') == "on" else False
        cctv = True if request.form.get('cctv') == "on" else False
        bed = True if request.form.get('bed') == "on" else False
        porch = True if request.form.get('porch') == "on" else False
        kids_pool = True if request.form.get('kids-pool') == "on" else False
        cold_water_pool = True if request.form.get('cold-water-pool') == "on" else False
        air_hockey = True if request.form.get('air-hockey') == "on" else False
        jacuzzi_tub = True if request.form.get('jacuzzi-tub') == "on" else False
        pets = True if request.form.get('pets') == "on" else False
        seremony = True if request.form.get('seremony') == "on" else False
        mci_anten = True if request.form.get('mci-anten') == "on" else False
        irancell_anten = True if request.form.get('irancell-anten') == "on" else False
        mci_net = True if request.form.get('mci-net') == "on" else False
        irancell_net = True if request.form.get('irancell-net') == "on" else False
        sanitary_facilities = request.form['sanitary-facilities']
        hall_facilities = request.form['hall-facilities']
        hall_heater = request.form['hall-heater']
        hall_cooler = request.form['hall-cooler']
        room_heater = request.form['room-heater']
        room_cooler = request.form['room-cooler']
        garden = request.form['garden']
        yard = request.form['yard']
        garden_facilities = request.form['garden-facilities']
        garden_description = request.form['garden-description']
        view = request.form['view']
        Prosperity_facilities = request.form['prosperity-facilities']
        joy_facilities = request.form['joy-facilities']
        cooking_facilities = request.form['cooking-facilities']
        dishes = request.form['dishes']
        entrance_steps = request.form['entrance-steps']
        enter_hour = request.form['enter-hour']
        exit_hour = request.form['exit-hour']
        min_stay = request.form['min-stay']
        max_stay = request.form['max-stay']
        last_calender_available = request.form['last-date-available']
        cancel_rules = request.form['cancel-rules']
        required_documents = request.form['required-docs']
        pets_rules = request.form['pets-rules']
        seremony_conditions = request.form['seremony-conditions']
        other_rules = request.form['other-rules']
        host_code = request.form['host-code']
        host_name = request.form['host-name']
        suggested_price = request.form['suggested-price']
        other_description = request.form['other-description']
        total_floors = request.form['total-floors']
        if not phone:
            flash('شماره تلفن الزامی است!')
        else:
            attr_dict = dict(agent_name=agent_name, agent_phone=agent_phone, phone=phone, title=title,
                             province=province, city=city, village=village, address=address, floor=floor, number=number,
                             postal_code=postal_code, ownership_type=ownership_type, environment_type=environment_type,
                             access_path=access_path, access_description=access_description,
                             neighbourhoodship=neighbourhoodship, distance_to_places=distance_to_places, walls=walls,
                             unit_area=unit_area, total_area=total_area, capacity=capacity, max_capacity=max_capacity,
                             rooms=rooms, sleep_services=sleep_services, single_bed=single_bed, double_bed=double_bed,
                             folding_sofa=folding_sofa, wc_number=wc_number, sanitary_facilities=sanitary_facilities,
                             pool=pool, dry_sauna=dry_sauna, wet_sauna=wet_sauna, parking=parking, balcony=balcony,
                             elders_reception=elders_reception, disabled_reception=disabled_reception, tv=tv,
                             digital_reciever=digital_reciever, refrigerator=refrigerator, oven=oven,
                             dining_service=dining_service, furniture=furniture, vacuum_machine=vacuum_machine,
                             persian_toilet=persian_toilet, toilet=toilet, bathroom=bathroom,
                             dining_furniture=dining_furniture, private_yard=private_yard, elevator=elevator,
                             evaporative_cooler=evaporative_cooler, air_conditioner=air_conditioner, radiator=radiator,
                             fireplace=fireplace, freewifi=freewifi, iron=iron, washing_machine=washing_machine,
                             jacuzzi=jacuzzi, microwave=microwave, barbecue=barbecue, bathtub=bathtub,
                             tea_maker=tea_maker, boardgame=boardgame, pingpong=pingpong, sound_system=sound_system,
                             billiards=billiards, table_football=table_football, game_console=game_console, cctv=cctv,
                             bed=bed, porch=porch, kids_pool=kids_pool, cold_water_pool=cold_water_pool,
                             air_hockey=air_hockey, jacuzzi_tub=jacuzzi_tub, pets=pets, seremony=seremony,
                             mci_anten=mci_anten, irancell_anten=irancell_anten, mci_net=mci_net,
                             irancell_net=irancell_net, hall_facilities=hall_facilities, hall_heater=hall_heater,
                             hall_cooler=hall_cooler,
                             room_heater=room_heater, room_cooler=room_cooler, garden=garden, yard=yard,
                             garden_facilities=garden_facilities, garden_description=garden_description, view=view,
                             Prosperity_facilities=Prosperity_facilities, joy_facilities=joy_facilities,
                             cooking_facilities=cooking_facilities, dishes=dishes, entrance_steps=entrance_steps,
                             enter_hour=enter_hour, exit_hour=exit_hour, min_stay=min_stay, max_stay=max_stay,
                             last_calender_available=last_calender_available, cancel_rules=cancel_rules,
                             required_documents=required_documents, pets_rules=pets_rules,
                             seremony_conditions=seremony_conditions, other_rules=other_rules, host_code=host_code,
                             host_name=host_name, suggested_price=suggested_price, other_description=other_description,
                             total_floors=total_floors)
            for key, value in attr_dict.items():
                if value == '':
                    attr_dict[key] = None
            file = Files(AgentName=attr_dict['agent_name'],
                         AgentPhone=attr_dict['agent_phone'],
                         Phone=attr_dict['phone'],
                         Media=[],
                         Title=attr_dict['title'],
                         Province=attr_dict['province'],
                         City=attr_dict['city'],
                         Village=attr_dict['village'],
                         Address=attr_dict['address'],
                         Floor=attr_dict['floor'],
                         TotalFloors=attr_dict['total_floors'],
                         HouseNumber=attr_dict['number'],
                         PostalCode=attr_dict['postal_code'],
                         OwnershipType=attr_dict['ownership_type'],
                         EnvironmentType=attr_dict['environment_type'],
                         AccessPath=attr_dict['access_path'],
                         AccessDescription=attr_dict['access_description'],
                         NeighbourhoodShip=attr_dict['neighbourhoodship'],
                         DistanceToPlaces=attr_dict['distance_to_places'],
                         Walls=attr_dict['walls'],
                         UnitArea=attr_dict['unit_area'],
                         TotalArea=attr_dict['total_area'],
                         Capacity=attr_dict['capacity'],
                         MaxCapacity=attr_dict['max_capacity'],
                         Rooms=attr_dict['rooms'],
                         SleepServices=attr_dict['sleep_services'],
                         SingleBed=attr_dict['single_bed'],
                         DoubleBed=attr_dict['double_bed'],
                         FoldingSofa=attr_dict['folding_sofa'],
                         WCQuantity=attr_dict['wc_number'],
                         SanitaryFacilities=attr_dict['sanitary_facilities'],
                         Pool=attr_dict['pool'],
                         DrySauna=attr_dict['dry_sauna'],
                         WetSauna=attr_dict['wet_sauna'],
                         Parking=attr_dict['parking'],
                         Balcony=attr_dict['balcony'],
                         EldersReception=attr_dict['elders_reception'],
                         DisabledReception=attr_dict['disabled_reception'],
                         TV=attr_dict['tv'],
                         DigitalReciever=attr_dict['digital_reciever'],
                         Refrigerator=attr_dict['refrigerator'],
                         Oven=attr_dict['oven'],
                         DiningService=attr_dict['dining_service'],
                         Furniture=attr_dict['furniture'],
                         VacuumMachine=attr_dict['vacuum_machine'],
                         PersianToilet=attr_dict['persian_toilet'],
                         Toilet=attr_dict['toilet'],
                         Bathroom=attr_dict['bathroom'],
                         DiningFurniture=attr_dict['dining_furniture'],
                         PrivateYard=attr_dict['private_yard'],
                         Elevator=attr_dict['elevator'],
                         EvaporativeCooler=attr_dict['evaporative_cooler'],
                         AirConditioner=attr_dict['air_conditioner'],
                         Radiator=attr_dict['radiator'],
                         Fireplace=attr_dict['fireplace'],
                         FreeWifi=attr_dict['freewifi'],
                         Iron=attr_dict['iron'],
                         WashingMachine=attr_dict['washing_machine'],
                         Jacuzzi=attr_dict['jacuzzi'],
                         Microwave=attr_dict['microwave'],
                         Barbecue=attr_dict['barbecue'],
                         Bathtub=attr_dict['bathtub'],
                         TeaMaker=attr_dict['tea_maker'],
                         BoardGame=attr_dict['boardgame'],
                         PingPong=attr_dict['pingpong'],
                         SoundSystem=attr_dict['sound_system'],
                         Billiards=attr_dict['billiards'],
                         TableFootball=attr_dict['table_football'],
                         GameConsole=attr_dict['game_console'],
                         CCTV=attr_dict['cctv'],
                         Bed=attr_dict['bed'],
                         Porch=attr_dict['porch'],
                         KidsPool=attr_dict['kids_pool'],
                         ColdWaterPool=attr_dict['cold_water_pool'],
                         AirHockey=attr_dict['air_hockey'],
                         JacuzziTub=attr_dict['jacuzzi_tub'],
                         Pets=attr_dict['pets'],
                         Seremony=attr_dict['seremony'],
                         MCIAnten=attr_dict['mci_anten'],
                         IrancellAnten=attr_dict['irancell_anten'],
                         MCINet=attr_dict['mci_net'],
                         IrancellNet=attr_dict['irancell_net'],
                         HallFacilities=attr_dict['hall_facilities'],
                         HallHeater=attr_dict['hall_heater'],
                         HallCooler=attr_dict['hall_cooler'],
                         RoomHeater=attr_dict['room_heater'],
                         RoomCooler=attr_dict['room_cooler'],
                         Yard=attr_dict['yard'],
                         Garden=attr_dict['garden'],
                         GardenFacilities=attr_dict['garden_facilities'],
                         GardenDescription=attr_dict['garden_description'],
                         View=attr_dict['view'],
                         ProsperityFacilities=attr_dict['Prosperity_facilities'],
                         JoyFacilities=attr_dict['joy_facilities'],
                         CookingFacilities=attr_dict['cooking_facilities'],
                         Dishes=attr_dict['dishes'],
                         EntranceSteps=attr_dict['entrance_steps'],
                         EnterHour=attr_dict['enter_hour'],
                         ExitHour=attr_dict['exit_hour'],
                         MinStay=attr_dict['min_stay'],
                         MaxStay=attr_dict['max_stay'],
                         LastCalenderAvailable=attr_dict['last_calender_available'],
                         CancelRules=attr_dict['cancel_rules'],
                         RequiredDocuments=attr_dict['required_documents'],
                         PetsRules=attr_dict['pets_rules'],
                         SeremonyConditions=attr_dict['seremony_conditions'],
                         OtherRules=attr_dict['other_rules'],
                         HostCode=attr_dict['host_code'],
                         HostName=attr_dict['host_name'],
                         SuggestedPrice=attr_dict['suggested_price'],
                         OtherDescriptions=attr_dict['other_description'],
                         LastUpdate=datetime.datetime.utcnow())
            db.session.add(file)
            db.session.commit()
            cur_user = {'user_id': current_user.id, 'username': current_user.username}
            logger.warning(f"{file} added by user {cur_user}")
            return redirect(url_for('index'))
    return render_template('create.html', now_time=datetime.datetime.now())


@app.route('/edit/<int:id>/', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = get_post(id)
    if request.method == 'POST':
        agent_name = request.form['agent-name']
        agent_phone = request.form['agent-phone']
        phone = request.form['phone']
        title = request.form['title']
        province = request.form['province']
        city = request.form['city']
        village = request.form['village']
        address = request.form['address']
        floor = request.form['floor']
        number = request.form['house-number']
        postal_code = request.form['postal-code']
        ownership_type = request.form['ownership-type']
        environment_type = request.form['environment-type']
        access_path = request.form['access-path']
        access_description = request.form['access-description']
        neighbourhoodship = request.form['neighbourhoodship']
        distance_to_places = request.form['distance-to-places']
        walls = request.form['walls']
        unit_area = request.form['unit-area']
        total_area = request.form['total-area']
        capacity = request.form['capacity']
        max_capacity = request.form['max-capacity']
        rooms = request.form['rooms']
        sleep_services = request.form['sleep-services']
        single_bed = request.form['single-bed']
        double_bed = request.form['double-bed']
        folding_sofa = request.form['folding-sofa']
        wc_number = request.form['wc']
        sanitary_facilities = request.form['sanitary-facilities']
        pool = True if request.form.get('pool') else False
        dry_sauna = True if request.form.get('dry-sauna') == "on" else False
        wet_sauna = True if request.form.get('wet-sauna') == "on" else False
        parking = True if request.form.get('parking') == "on" else False
        balcony = True if request.form.get('balcony') == "on" else False
        elders_reception = True if request.form.get('elders-reception') == "on" else False
        disabled_reception = True if request.form.get('disabled-reception') == "on" else False
        tv = True if request.form.get('tv') == "on" else False
        digital_reciever = True if request.form.get('digital-reciever') == "on" else False
        refrigerator = True if request.form.get('refrigerator') == "on" else False
        oven = True if request.form.get('oven') == "on" else False
        dining_service = True if request.form.get('dining-service') == "on" else False
        furniture = True if request.form.get('furniture') == "on" else False
        vacuum_machine = True if request.form.get('vacuum-machine') == "on" else False
        persian_toilet = True if request.form.get('persian-toilet') == "on" else False
        toilet = True if request.form.get('toilet') == "on" else False
        bathroom = True if request.form.get('bathroom') == "on" else False
        dining_furniture = True if request.form.get('dining-furniture') == "on" else False
        private_yard = True if request.form.get('private-yard') == "on" else False
        elevator = True if request.form.get('elevator') == "on" else False
        evaporative_cooler = True if request.form.get('evaporative-cooler') == "on" else False
        air_conditioner = True if request.form.get('air-conditioner') == "on" else False
        radiator = True if request.form.get('radiator') == "on" else False
        fireplace = True if request.form.get('fireplace') == "on" else False
        freewifi = True if request.form.get('freewifi') == "on" else False
        iron = True if request.form.get('iron') == "on" else False
        washing_machine = True if request.form.get('washing-machine') == "on" else False
        jacuzzi = True if request.form.get('jacuzzi') == "on" else False
        microwave = True if request.form.get('microwave') == "on" else False
        barbecue = True if request.form.get('barbecue') == "on" else False
        bathtub = True if request.form.get('bathtub') == "on" else False
        tea_maker = True if request.form.get('tea-maker') == "on" else False
        boardgame = True if request.form.get('boardgame') == "on" else False
        pingpong = True if request.form.get('pingpong') == "on" else False
        sound_system = True if request.form.get('sound-system') == "on" else False
        billiards = True if request.form.get('billiards') == "on" else False
        table_football = True if request.form.get('table-football') == "on" else False
        game_console = True if request.form.get('game-console') == "on" else False
        cctv = True if request.form.get('cctv') == "on" else False
        bed = True if request.form.get('bed') == "on" else False
        porch = True if request.form.get('porch') == "on" else False
        kids_pool = True if request.form.get('kids-pool') == "on" else False
        cold_water_pool = True if request.form.get('cold-water-pool') == "on" else False
        air_hockey = True if request.form.get('air-hockey') == "on" else False
        jacuzzi_tub = True if request.form.get('jacuzzi-tub') == "on" else False
        pets = True if request.form.get('pets') == "on" else False
        seremony = True if request.form.get('seremony') == "on" else False
        mci_anten = True if request.form.get('mci-anten') == "on" else False
        irancell_anten = True if request.form.get('irancell-anten') == "on" else False
        mci_net = True if request.form.get('mci-net') == "on" else False
        irancell_net = True if request.form.get('irancell-net') == "on" else False
        sanitary_facilities = request.form['sanitary-facilities']
        hall_facilities = request.form['hall-facilities']
        hall_heater = request.form['hall-heater']
        hall_cooler = request.form['hall-cooler']
        room_heater = request.form['room-heater']
        room_cooler = request.form['room-cooler']
        garden = request.form['garden']
        yard = request.form['yard']
        garden_facilities = request.form['garden-facilities']
        garden_description = request.form['garden-description']
        view = request.form['view']
        Prosperity_facilities = request.form['prosperity-facilities']
        joy_facilities = request.form['joy-facilities']
        cooking_facilities = request.form['cooking-facilities']
        dishes = request.form['dishes']
        entrance_steps = request.form['entrance-steps']
        enter_hour = request.form['enter-hour']
        exit_hour = request.form['exit-hour']
        min_stay = request.form['min-stay']
        max_stay = request.form['max-stay']
        last_calender_available = request.form['last-date-available']
        cancel_rules = request.form['cancel-rules']
        required_documents = request.form['required-docs']
        pets_rules = request.form['pets-rules']
        seremony_conditions = request.form['seremony-conditions']
        other_rules = request.form['other-rules']
        host_code = request.form['host-code']
        host_name = request.form['host-name']
        suggested_price = request.form['suggested-price']
        other_description = request.form['other-description']
        total_floors = request.form['total-floors']
        file = db.session.query(Files).filter(Files.Id == id).first()
        file.AgentName = agent_name
        file.AgentPhone = agent_phone
        file.Phone = phone
        # file.Media = media
        file.Title = title
        file.Province = province
        file.City = city
        file.Village = village
        file.Address = address
        file.Floor = floor
        file.TotalFloors = total_floors
        file.HouseNumber = number
        file.PostalCode = postal_code
        file.OwnershipType = ownership_type
        file.EnvironmentType = environment_type
        file.AccessPath = access_path
        file.AccessDescription = access_description
        file.NeighbourhoodShip = neighbourhoodship
        file.DistanceToPlaces = distance_to_places
        file.Walls = walls
        file.UnitArea = unit_area
        file.TotalArea = total_area
        file.Capacity = capacity
        file.MaxCapacity = max_capacity
        file.Rooms = rooms
        file.SleepServices = sleep_services
        file.SingleBed = single_bed
        file.DoubleBed = double_bed
        file.FoldingSofa = folding_sofa
        file.WCQuantity = wc_number
        file.SanitaryFacilities = sanitary_facilities
        file.Pool = pool
        file.DrySauna = dry_sauna
        file.WetSauna = wet_sauna
        file.Parking = parking
        file.Balcony = balcony
        file.EldersReception = elders_reception
        file.DisabledReception = disabled_reception
        file.TV = tv
        file.DigitalReciever = digital_reciever
        file.Refrigerator = refrigerator
        file.Oven = oven
        file.DiningService = dining_service
        file.Furniture = furniture
        file.VacuumMachine = vacuum_machine
        file.PersianToilet = persian_toilet
        file.Toilet = toilet
        file.Bathroom = bathroom
        file.DiningFurniture = dining_furniture
        file.PrivateYard = private_yard
        file.Elevator = elevator
        file.EvaporativeCooler = evaporative_cooler
        file.AirConditioner = air_conditioner
        file.Radiator = radiator
        file.Fireplace = fireplace
        file.FreeWifi = freewifi
        file.Iron = iron
        file.WashingMachine = washing_machine
        file.Jacuzzi = jacuzzi
        file.Microwave = microwave
        file.Barbecue = barbecue
        file.Bathtub = bathtub
        file.TeaMaker = tea_maker
        file.BoardGame = boardgame
        file.PingPong = pingpong
        file.SoundSystem = sound_system
        file.Billiards = billiards
        file.TableFootball = table_football
        file.GameConsole = game_console
        file.CCTV = cctv
        file.Bed = bed
        file.Porch = porch
        file.KidsPool = kids_pool
        file.ColdWaterPool = cold_water_pool
        file.AirHockey = air_hockey
        file.JacuzziTub = jacuzzi_tub
        file.Pets = pets
        file.Seremony = seremony
        file.MCIAnten = mci_anten
        file.IrancellAnten = irancell_anten
        file.MCINet = mci_net
        file.IrancellNet = irancell_net
        file.HallFacilities = hall_facilities
        file.HallHeater = hall_heater
        file.HallCooler = hall_cooler
        file.RoomHeater = room_heater
        file.RoomCooler = room_cooler
        file.Yard = yard
        file.Garden = garden
        file.GardenFacilities = garden_facilities
        file.GardenDescription = garden_description
        file.View = view
        file.ProsperityFacilities = Prosperity_facilities
        file.JoyFacilities = joy_facilities
        file.CookingFacilities = cooking_facilities
        file.Dishes = dishes
        file.EntranceSteps = entrance_steps
        file.EnterHour = enter_hour
        file.ExitHour = exit_hour
        file.MinStay = min_stay
        file.MaxStay = max_stay
        file.LastCalenderAvailable = last_calender_available
        file.CancelRules = cancel_rules
        file.RequiredDocuments = required_documents
        file.PetsRules = pets_rules
        file.SeremonyConditions = seremony_conditions
        file.OtherRules = other_rules
        file.HostCode = host_code
        file.HostName = host_name
        file.SuggestedPrice = suggested_price
        file.OtherDescriptions = other_description
        file.LastUpdate = datetime.datetime.utcnow()
        db.session.commit()
        cur_user = {'user_id': current_user.id, 'username': current_user.username}
        logger.warning(f"{file} edited by user {cur_user}")
        return redirect(url_for('index'))
    return render_template('edit.html', post=post, now_time=datetime.datetime.now())


@app.route('/delete_post/<int:id>/', methods=('GET', 'POST'))
@login_required
def delete_post(id):
    file = db.session.query(Files).filter(Files.Id == id).first()
    db.session.query(Files).filter(Files.Id == id).delete()
    cur_user = {'user_id': current_user.id, 'username': current_user.username}
    logger.warning(f"{file} deleted by user {cur_user}")
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/upload/<int:id>/', methods=['GET', 'POST'])
@login_required
def upload_image(id):
    post = get_post(id)
    if request.method == 'POST':
        files = request.files.get('file')
        addresses = list()
        counter = 0
        for file in request.files.getlist('file'):
            newpath = f'{UPLOAD_FOLDER}{id}'
            image_path = f'uploads/{id}'
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            repeated = True
            while repeated:
                if os.path.exists(f"{newpath}/image{counter}.{file.filename.split('.')[-1]}"):
                    counter += 1
                else:
                    repeated = False
            file.save(f"{newpath}/image{counter}.{file.filename.split('.')[-1]}")
            addresses.append(f"{image_path}/image{counter}.{file.filename.split('.')[-1]}")
            flash('Image successfully uploaded and displayed below')
        addresses = [image_path + '/' + i for i in os.listdir(f'static/uploads/{id}/')]
        db_file = db.session.query(Files).filter(Files.Id == id).first()
        new_file = list()
        for i in addresses:
            new_file.append(i)
        new_file.extend(db_file.Media)
        db_file.Media = addresses
        db.session.commit()
        cur_user = {'user_id': current_user.id, 'username': current_user.username}
        logger.warning(f"media uploaded for {db_file} by user {cur_user}")
        return redirect(url_for('index'))
    return render_template('upload-image.html', post=post)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
