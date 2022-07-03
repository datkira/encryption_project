import base64
import hashlib
import os
import tkinter as tk
import uuid
from base64 import b64encode
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfile
import pymysql
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from cryptography.hazmat.backends import default_backend as crypto_default_backend, default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from dotenv import load_dotenv

load_dotenv()
# need to create database "encryption_project" from command line before running this program
db = pymysql.connect(host=os.getenv('HOST'), user=os.getenv('DATABASE_USER'), passwd=os.getenv('DATABASE_PASSWORD'),
                     db=os.getenv('DATABASE_NAME'))
cursor = db.cursor()

# set email variable to null
emailGlobal = None


def loadModel():
    # create user table if not exists
    cursor.execute("""CREATE TABLE IF NOT EXISTS user (
        id INT(11) NOT NULL AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        phone VARCHAR(255) NOT NULL,
        dob VARCHAR(255) NOT NULL,
        data VARCHAR(255) ,
        data_encrypt VARCHAR(255) ,
        key_public VARCHAR(2048) NOT NULL,
        key_private VARCHAR(2048) NOT NULL,
        vector_iv VARCHAR(2048) ,
        PRIMARY KEY (username)
    )""")


# You can also use a pandas dataframe for pokemon_info.
# you can convert the dataframe using df.to_numpy.tolist()
pokemon_info = []

frame_styles = {"relief": "groove",
                "bd": 3,
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}


class LoginPage(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#708090", height=431, width=626)  # this is the background
        main_frame.pack(fill="both", expand="true")

        self.geometry("626x431")  # Sets window size to 626w x 431h pixels
        self.resizable(0, 0)  # This prevents any resizing of the screen
        title_styles = {"font": ("Trebuchet MS Bold", 16), "background": "white", "fg": "black"}

        text_styles = {"font": ("Verdana", 14)
            , "background": "white", "fg": "black"}

        frame_login = tk.Frame(main_frame, bg="white", relief="groove",
                               bd=2)  # this is the frame that holds all the login details and buttons
        frame_login.place(rely=0.30, relx=0.17, height=130, width=400)

        label_title = tk.Label(frame_login, title_styles, text="Login Page")
        label_title.grid(row=0, column=0, columnspan=1)

        label_email = tk.Label(frame_login, text_styles, text="Email:")
        label_email.grid(row=1, column=0)

        label_pw = tk.Label(frame_login, text_styles, text="Password:")
        label_pw.grid(row=2, column=0)

        entry_email = ttk.Entry(frame_login, width=45, cursor="xterm")
        entry_email.grid(row=1, column=1)

        entry_pw = ttk.Entry(frame_login, width=45, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1)

        button = ttk.Button(frame_login, text="Login", command=lambda: getLogin())
        button.place(rely=0.70, relx=0.50)

        signup_btn = ttk.Button(frame_login, text="Register", command=lambda: get_signup())
        signup_btn.place(rely=0.70, relx=0.75)

        def get_signup():
            SignupPage()

        def getLogin():
            email = entry_email.get()
            global emailGlobal  # this is used to set the email variable to the email entered in the login page
            emailGlobal = email
            password = entry_pw.get()

            if validate(email, password):
                tk.messagebox.showinfo("Login Successful", "Welcome {}".format(email))
                root.deiconify()
                top.destroy()
            else:
                tk.messagebox.showerror("Information", "The Username or Password you have entered are incorrect ")

        def validate(email, password):
            # check if username and password are in the database
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user is None:
                return False
            else:
                if check_password(user[2], password):
                    # signFileSHA256()
                    # verifySignSHA256()
                    return True
                else:
                    return False


class SignupPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#3F6BAA", height=150, width=250)
        # pack_propagate prevents the window resizing to match the widgets
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")

        self.geometry("250x150")
        self.resizable(0, 0)

        self.title("Registration")

        text_styles = {"font": ("Verdana", 10),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}

        label_email = tk.Label(main_frame, text_styles, text="New Email:")
        label_email.grid(row=1, column=0)

        label_pw = tk.Label(main_frame, text_styles, text="New Password:")
        label_pw.grid(row=2, column=0)

        label_name = tk.Label(main_frame, text_styles, text="Name:")
        label_name.grid(row=3, column=0)

        # date of birth
        label_dob = tk.Label(main_frame, text_styles, text="Date of Birth:")
        label_dob.grid(row=4, column=0)

        # phone
        label_phone = tk.Label(main_frame, text_styles, text="Phone:")
        label_phone.grid(row=5, column=0)

        # address
        label_address = tk.Label(main_frame, text_styles, text="Address:")
        label_address.grid(row=6, column=0)

        entry_email = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_email.grid(row=1, column=1)

        entry_pw = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1)

        entry_name = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_name.grid(row=3, column=1)

        entry_dob = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_dob.grid(row=4, column=1)

        entry_phone = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_phone.grid(row=5, column=1)

        entry_address = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_address.grid(row=6, column=1)

        button = ttk.Button(main_frame, text="Register", command=lambda: signup())
        button.grid(row=7, column=1)

        def signup():
            # Creates a text file with the Username and password
            email = entry_email.get()
            pw = entry_pw.get()
            name = entry_name.get()
            dob = entry_dob.get()
            phone = entry_phone.get()
            address = entry_address.get()
            validation = validate_user(email)
            if not validation:
                tk.messagebox.showerror("Information", "That Username already exists")
            else:
                password = hash_password(pw)
                # log password console

                credentials = open("credentials.txt", "a")
                credentials.write(f"Email,{email},Password,{pw},\n")
                keypublic, keyprivate = generate_keypair()
                credentials.write(f"Keypublic,{keypublic},keyprivate,{keyprivate},\n")
                credentials.close()
                credentials = open("credentials.txt", "a")
                keyprivate, vector = EncryptAES(keyprivate, password)
                credentials.close()
                sql = "INSERT INTO user (email, password, name, dob, phone, address, key_public, key_private, vector_iv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (email, password, name, dob, phone, address, keypublic, keyprivate, vector)
                cursor.execute(sql, val)
                db.commit()
                tk.messagebox.showinfo("Registration Successful", "Welcome {}".format(email))
                global emailGlobal
                emailGlobal = email
                root.deiconify()
                top.destroy()

        def validate_user(email):
            # check if the username is already in the database
            user = cursor.execute("SELECT * FROM user WHERE email = '%s'" % email)

            if user:
                return False
            else:
                return True

        def generate_keypair():
            key = rsa.generate_private_key(
                backend=crypto_default_backend(),
                public_exponent=65537,
                key_size=2048
            )
            private_key = key.private_bytes(
                crypto_serialization.Encoding.PEM,
                crypto_serialization.PrivateFormat.TraditionalOpenSSL,
                crypto_serialization.NoEncryption()
            )
            public_key = key.public_key().public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH
            ).decode('utf-8')
            return (public_key, private_key)

        def EncryptAES(key, password):
            secret_key = password[0:16].encode('utf-8')
            cipher = AES.new(secret_key, AES.MODE_CBC)
            data_encrypt = cipher.encrypt(pad(key, AES.block_size))
            iv = b64encode(cipher.iv).decode('utf-8')
            data_encrypt = key.decode('utf-8')
            return data_encrypt, iv

        def DecryptAES(data_encrypt, password, iv):
            secret_key = password[0:16].encode('utf-8')
            cipher = AES.new(secret_key, AES.MODE_CBC, iv)
            data = unpad(cipher.decrypt(data_encrypt), AES.block_size)
            return data
            return data_encrypt, iv


class UpdatePageRegular(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#3F6BAA")
        # pack_propagate prevents the window resizing to match the widgets
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")

        self.geometry("250x150")
        self.resizable(0, 0)

        self.title("Update information")

        text_styles = {"font": ("Verdana", 10),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}
        label_name = tk.Label(main_frame, text_styles, text="Name:")
        label_name.grid(row=3, column=0)

        # date of birth
        label_dob = tk.Label(main_frame, text_styles, text="Date of Birth:")
        label_dob.grid(row=4, column=0)

        # phone
        label_phone = tk.Label(main_frame, text_styles, text="Phone:")
        label_phone.grid(row=5, column=0)

        # address
        label_address = tk.Label(main_frame, text_styles, text="Address:")
        label_address.grid(row=6, column=0)

        cursor.execute("SELECT * FROM user WHERE email = '%s'" % emailGlobal)
        user = cursor.fetchone()
        # set default values for the fields
        entry_name = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_name.insert(0, user[3])
        entry_name.grid(row=3, column=1)

        entry_dob = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_dob.insert(0, user[6])
        entry_dob.grid(row=4, column=1)

        entry_phone = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_phone.insert(0, user[5])
        entry_phone.grid(row=5, column=1)

        entry_address = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_address.insert(0, user[4])
        entry_address.grid(row=6, column=1)

        button = ttk.Button(main_frame, text="Update regular", command=lambda: update())
        button.grid(row=7, column=1)

        def update():
            # Creates a text file with the Username and password
            name = entry_name.get()
            dob = entry_dob.get()
            phone = entry_phone.get()
            address = entry_address.get()
            # log password console
            sql = "UPDATE user SET name = %s, dob = %s, phone = %s, address = %s WHERE email = %s"
            val = (name, dob, phone, address, emailGlobal)
            cursor.execute(sql, val)
            db.commit()
            tk.messagebox.showinfo("Update Successfully", "You updated your information {}".format(emailGlobal))
            root.deiconify()


class UpdatePagePassword(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#3F6BAA")
        # pack_propagate prevents the window resizing to match the widgets
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")

        self.geometry("250x150")
        self.resizable(0, 0)

        self.title("Update information")

        text_styles = {"font": ("Verdana", 10),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}

        label_pw = tk.Label(main_frame, text_styles, text="New Password:")
        label_pw.grid(row=2, column=0)

        entry_pw = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1)

        button = ttk.Button(main_frame, text="Update password", command=lambda: update())
        button.grid(row=7, column=1)

        def update():  # @TODO update the password
            password = entry_pw.get()
            # Trường hợp đổi passphase cần đảm bảo cặp khoá Kprivate, Kpublic không bị thay đổi. Tức
            # là khoá Kprivate được mã hoá ở bước 2.2 với passphase cũ, cần được mã hoá lại với
            # passphase mới


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Menu1", menu=menu_file)
        menu_file.add_command(label="All Widgets", command=lambda: parent.show_frame(Some_Widgets))
        menu_file.add_separator()
        menu_file.add_command(label="Exit Application", command=lambda: parent.Quit_application())

        menu_orders = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Menu2", menu=menu_orders)

        menu_pricing = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Menu3", menu=menu_pricing)
        menu_pricing.add_command(label="Page One", command=lambda: parent.show_frame(PageOne))

        menu_operations = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Menu4", menu=menu_operations)
        menu_operations.add_command(label="Page Two", command=lambda: parent.show_frame(PageTwo))
        menu_positions = tk.Menu(menu_operations, tearoff=0)
        menu_operations.add_cascade(label="Menu5", menu=menu_positions)
        menu_positions.add_command(label="Page Three", command=lambda: parent.show_frame(PageThree))
        menu_positions.add_command(label="Page Four", command=lambda: parent.show_frame(PageFour))

        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Update information", menu=menu_help)
        menu_help.add_command(label="Change information regular", command=lambda: parent.ChangeInformationRegular())
        menu_help.add_command(label="Change information password", command=lambda: parent.ChangeInformationPassword())


def hash_password(text):
    """
        Basic hashing function for a text using random unique salt.
    """
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + text.encode()).hexdigest() + ':' + salt


def check_password(hashedText, providedText):
    """
        Check for the text in the hashed text
    """
    _hashedText, salt = hashedText.split(':')
    return _hashedText == hashlib.sha256(salt.encode() + providedText.encode()).hexdigest()


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        # self.resizable(0, 0) prevents the app from being resized
        # self.geometry("1024x600") fixes the applications size
        self.frames = {}
        pages = (Some_Widgets, PageOne, PageTwo, PageThree, PageFour)
        for F in pages:
            frame = F(main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Some_Widgets)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def ChangeInformationRegular(self):
        UpdatePageRegular()

    def ChangeInformationPassword(self):
        UpdatePagePassword()

    def Quit_application(self):
        self.destroy()


class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.main_frame = tk.Frame(self, bg="#BEB2A7", height=600, width=1024)
        # self.main_frame.pack_propagate(0)
        self.main_frame.pack(fill="both", expand="true")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


class Some_Widgets(GUI):  # inherits from the GUI class

    def __init__(self, parent, controller):
        def Encryptfile():
            key_session = get_random_bytes(16)
            cipher = AES.new(key_session, AES.MODE_CBC)
            messagebox.showinfo("", "select one or more files to encrypt")
            filepath = filedialog.askopenfilenames()
            for x in filepath:
                with open(x, "rb") as file:
                    original = file.read()
                    data_encrypt = cipher.encrypt(pad(original, AES.block_size))
                    iv = b64encode(cipher.iv)
                with open(x, "wb") as encrypted_file:
                    encrypted_file.write(data_encrypt)
                    # encrypted_file.write(b"\n")
                    # encrypted_file.write(key_session)
            if not filepath:
                messagebox.showerror("Error", "no file was selected, try again")
            else:
                messagebox.showinfo("", "files encrypted successfully!")
            return key_session, iv

        def Decryptfile(key_session, iv):
            messagebox.showinfo("", "select one or more files to decrypt")
            filepath = filedialog.askopenfilenames()
            cipher = AES.new(key_session, AES.MODE_CBC, iv)
            for x in filepath:
                with open(x, "rb") as file:
                    original = file.read()
                    data_decrypt = unpad(cipher.decrypt(original), AES.block_size)

        def SignFile():
            messagebox.showinfo("", "select one or more files to sign")
            filepath = filedialog.askopenfilenames()
            for x in filepath:
                cursor.execute("SELECT * FROM user WHERE email = %s", (emailGlobal,))
                user = cursor.fetchone()
                print(user[10])
                private_key = serialization.load_pem_private_key(
                    user[10].encode('ascii'),
                    password=None,
                    backend=default_backend(),
                )

                # Create new sign file and write the data to it
                with open(x, "rb") as fileOrigin:
                    payload = fileOrigin.read()
                    print(payload)

                # Sign the payload file.
                signature = base64.b64encode(
                    private_key.sign(
                        payload,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )
                )

                with open(x + ".sign", 'wb') as sign_file:
                    sign_file.write(signature)
            if not filepath:
                messagebox.showerror("Error", "no file was selected, try again")
            else:
                messagebox.showinfo("", "files sign successfully!")
            return True

        def VerifySignSHA256():
            messagebox.showinfo("", "select one or more files to sign")
            filepath = filedialog.askopenfilenames()
            # Load the public key.
            cursor.execute("SELECT * FROM user WHERE email = %s", (emailGlobal,))
            user = cursor.fetchone()
            print('filepath: ', filepath)
            for x in filepath:
                public_key = load_pem_public_key(user[9].encode('ascii'), default_backend())
                # Load the payload contents and the signature.
                with open(x, 'rb') as f:
                    payload_contents = f.read()
                with open('signature.sig', 'rb') as f:
                    signature = base64.b64decode(f.read())

                    # Perform the verification.
                    public_key.verify(
                        signature,
                        payload_contents,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )

        GUI.__init__(self, parent)

        frame1 = tk.LabelFrame(self, frame_styles, text="This is a LabelFrame containing a Treeview")
        frame1.place(rely=0.05, relx=0.02, height=400, width=400)

        frame2 = tk.LabelFrame(self, frame_styles, text="Some widgets")
        frame2.place(rely=0.05, relx=0.45, height=500, width=500)

        button1 = tk.Button(frame2, text="upload file", command=lambda: Encryptfile())
        button1.pack()
        button2 = ttk.Button(frame2, text="upload file to sign", command=lambda: SignFile())
        button2.pack()
        button3 = ttk.Button(frame2, text="upload file to verify", command=lambda: VerifySignSHA256())
        button3.pack()

        Var1 = tk.IntVar()
        Var2 = tk.IntVar()
        Cbutton1 = tk.Checkbutton(frame2, text="tk CheckButton1", variable=Var1, onvalue=1, offvalue=0)
        Cbutton1.pack()
        Cbutton2 = tk.Checkbutton(frame2, text="tk CheckButton2", variable=Var2, onvalue=1, offvalue=0)
        Cbutton2.pack()

        Cbutton3 = ttk.Checkbutton(frame2, text="ttk CheckButton1", variable=Var1, onvalue=1, offvalue=0)
        Cbutton3.pack()
        Cbutton3 = ttk.Checkbutton(frame2, text="ttk CheckButton2", variable=Var2, onvalue=1, offvalue=0)
        Cbutton3.pack()

        Lbox1 = tk.Listbox(frame2, selectmode="multiple")
        Lbox1.insert(1, "file1")
        Lbox1.insert(2, "file2")
        Lbox1.insert(3, "Python")
        Lbox1.insert(3, "StackOverflow")
        Lbox1.pack(side="left")

        Var3 = tk.IntVar()
        R1 = tk.Radiobutton(frame2, text="tk Radiobutton1", variable=Var3, value=1)
        R1.pack()
        R2 = tk.Radiobutton(frame2, text="tk Radiobutton2", variable=Var3, value=2)
        R2.pack()
        R3 = tk.Radiobutton(frame2, text="tk Radiobutton3", variable=Var3, value=3)
        R3.pack()

        R4 = tk.Radiobutton(frame2, text="ttk Radiobutton1", variable=Var3, value=1)
        R4.pack()
        R5 = tk.Radiobutton(frame2, text="ttk Radiobutton2", variable=Var3, value=2)
        R5.pack()
        R6 = tk.Radiobutton(frame2, text="ttk Radiobutton3", variable=Var3, value=3)
        R6.pack()

        # This is a treeview.
        tv1 = ttk.Treeview(frame1)
        column_list_account = ["Name", "Type", "Base Stat Total"]
        tv1['columns'] = column_list_account
        tv1["show"] = "headings"  # removes empty column
        for column in column_list_account:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.place(relheight=1, relwidth=0.995)
        treescroll = tk.Scrollbar(frame1)
        treescroll.configure(command=tv1.yview)
        tv1.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side="right", fill="y")

        def Load_data():
            for row in pokemon_info:
                tv1.insert("", "end", values=row)

        def Refresh_data():
            # Deletes the data in the current treeview and reinserts it.
            tv1.delete(*tv1.get_children())  # *=splat operator
            Load_data()

        Load_data()


class PageOne(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Page One")
        label1.pack(side="top")


class PageThree(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Page Three")
        label1.pack(side="top")


class PageFour(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Page Four")
        label1.pack(side="top")


class PageTwo(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Page Two")
        label1.pack(side="top")

    def open_file():
        file_path = askopenfile(mode='r', filetypes=[('Files to encrypt', '*doc')])
        if file_path is not None:
            pass


class OpenNewWindow(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.title("Here is the Title of the Window")
        self.geometry("500x500")
        self.resizable(0, 0)

        frame1 = ttk.LabelFrame(main_frame, text="This is a ttk LabelFrame")
        frame1.pack(expand=True, fill="both")

        label1 = tk.Label(frame1, font=("Verdana", 20), text="OpenNewWindow Page")
        label1.pack(side="top")


loadModel()

top = LoginPage()
top.title("Tkinter App Template - Login Page")
root = MyApp()
root.withdraw()
root.title("Tkinter App Template")

root.mainloop()
# disconnect from server
db.close()
