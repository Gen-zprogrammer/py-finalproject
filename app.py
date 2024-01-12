import qrcode #Membuat QR code
from flask import Flask, render_template, request, redirect, url_for, session #Menjalankan APK
from flask_sqlalchemy import SQLAlchemy #Utk Koneksi database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/kampus' #Library, username, passwd, localhost, nama database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Ketika ada kesalahan
app.config['SECRET_KEY'] = 'your_secret_key' #API
db = SQLAlchemy(app) #Data yang diconfig masuk ke var db

# Definisikan model-model SQLAlchemy
class Dosen(db.Model):  #Mengambil data dosen
    NIDN = db.Column(db.Integer, primary_key=True)
    PASSWORD = db.Column(db.String(255), nullable=False)
    Nama_dosen = db.Column(db.String(255), nullable=False)

class MataKuliah(db.Model):
    Kode_MK = db.Column(db.Integer, primary_key=True)
    Nama_MK = db.Column(db.String(255), nullable=False)

class DosenMataKuliah(db.Model):
    NIDN = db.Column(db.Integer, db.ForeignKey('dosen.NIDN'), primary_key=True)
    Kode_MK = db.Column(db.Integer, db.ForeignKey('mata_kuliah.Kode_MK'), primary_key=True)
    Jadwal_ID = db.Column(db.Integer, db.ForeignKey('jadwal.ID_Jadwal'))

class Jadwal(db.Model):
    ID_Jadwal = db.Column(db.Integer, primary_key=True)
    Kode_MK = db.Column(db.Integer, db.ForeignKey('mata_kuliah.Kode_MK'))
    NIDN = db.Column(db.Integer, db.ForeignKey('dosen.NIDN'))
    Hari = db.Column(db.String(10), nullable=False)
    Jam = db.Column(db.String(20), nullable=False)

# Fungsi untuk memeriksa jadwal yang valid 
def is_valid_schedule(nidn, kode_mk, current_day): 
    return Jadwal.query.filter_by(NIDN=nidn, Kode_MK=kode_mk, Hari=current_day).first() is not None

# Fungsi untuk mendapatkan pengguna saat ini/auto
def get_current_user():
    if 'nidn' in session:
        return Dosen.query.filter_by(NIDN=session['nidn']).first() #Ngefilter data dari NIDN 
    return None

# Fungsi untuk mendapatkan informasi kelas saat ini
def get_current_class_info():
    current_user = get_current_user()
    if current_user:
        dosen_mata_kuliah = DosenMataKuliah.query.filter_by(NIDN=current_user.NIDN).first()
        if dosen_mata_kuliah:
            kode_mk = dosen_mata_kuliah.Kode_MK
            return current_user, MataKuliah.query.filter_by(Kode_MK=kode_mk).first(), True

    return None, None, False

# Fungsi untuk membuat QR Code
def create_qr_code(kelas, dosen, hari, praktikum_ke, materi):
    data = f"Kelas: {kelas}\nDosen: {dosen}\nHari: {hari}\nPraktikum ke: {praktikum_ke}\nMateri: {materi}\nSelamat Anda Berhasil Absen!"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    #Memasukan data dari var data kedalam qrcode
    qr.add_data(data)
    qr.make(fit=True) 
    qrcode_img = qr.make_image(fill_color="black", back_color="white")
    file_name = f"qrcode_absen_{kelas}_{praktikum_ke}.png" #Sesuai nama file QRcode
    qrcode_filename = f"static/{file_name}" #Untuk memasukan folder static
    qrcode_img.save(qrcode_filename)
    return file_name

# Routing untuk mengarahkan ke halaman login
@app.route('/')
def redirect_to_login():
    return redirect(url_for('login'))

# Routing untuk halaman login
@app.route('/login', methods=['GET', 'POST']) #Membandingkan data yg diberikan dgn db 
def login():
    error_message = None

    if request.method == 'POST': 
        nidn = request.form['nidn'] 
        password = request.form['password']

        dosen = Dosen.query.filter_by(NIDN=nidn, PASSWORD=password).first()

        if dosen: #Mengambil data dari db berupa nama dosen dan dimunculkan ke index.html
            session['nidn'] = dosen.NIDN
            session['nama_dosen'] = dosen.Nama_dosen 
            return redirect(url_for('index'))
        else:
            error_message = 'Login failed. NIDN or password is incorrect.'

    return render_template('login.html', error_message=error_message)

# Routing untuk halaman index
@app.route('/index', methods=['GET', 'POST'])
def index():
    current_user, current_class, is_valid_schedule = get_current_class_info()

    current_professor = get_current_user()
    nama_dosen = current_professor.Nama_dosen if current_professor else ''

    if request.method == 'POST': #Mendapatkan data dari index.html dan kemudian diberikan ke fungsi membuat QRcode
        kelas = request.form['kelas']
        dosen = nama_dosen 
        hari = request.form['hari']
        praktikum_ke = request.form['praktikum_ke']
        materi = request.form['materi']

        if current_user and is_valid_schedule:
            qrcode_filename = create_qr_code(kelas, dosen, hari, praktikum_ke, materi)
            return render_template('result.html', file_name=qrcode_filename) #Ketika berhasil membuat QR codeakan berpindah ke result.html dan menampilkan QRcode nya
        else:
            error_message = 'Anda tidak memiliki kelas saat ini.'
            return render_template('error.html', error_message=error_message)

    return render_template( #Kalau terjadi error
        'index.html',
        current_user=current_user,
        current_class=current_class,
        is_valid_schedule=is_valid_schedule,
        nama_dosen=nama_dosen
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)  #Utk Run semua file app.py
