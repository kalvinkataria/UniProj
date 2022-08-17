import kivy
import mysql.connector
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import bcrypt
import re

mydb = mysql.connector.connect(
    host="co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com",
    user="admin",
    password="uuhg7K1I2Ep8gL9k0ddG"
)

class SigninApp(App):
    def build(self):
        pass

class P(FloatLayout):
    pass

class LoginPage(Screen):
    stored_username = None
    stored_email = None
    def validate_account(self, username, password):
        # Check if text inputs are not empty.
        if(username == "" or password == ""):
            self.show_popup("You are missing details.")
        else:
            cursor = mydb.cursor(buffered=True, dictionary=True)
            hashquery = "SELECT password FROM `university-review`.User WHERE username=%s"
            cursor.execute(hashquery, (username,))
            result = cursor.fetchall()
            if result:
                for x in result:
                    hashedpass = (x['password'])
                if bcrypt.checkpw(password.encode('utf-8'), hashedpass.encode('utf-8')):
                    self.ids.username_ti.text = ""
                    self.ids.password_ti.text = ""
                    self.stored_username = username
                    self.parent.current = "mainpage"
                    print(self.stored_username)
                else:
                    self.show_popup("Your username or password is wrong!")
            else:
                self.show_popup("Your username or password is wrong!")

    def show_popup(self, message):
        show = P()
        popupWindow = Popup(title="Error!", content=Label(text=message), size_hint=(None, None), size=(300, 150))
        popupWindow.open()  # show the popup

class RegisterPage(Screen):
    def register_account(self, username, email, password):
        if(username == "" or email == "" or password == ""):
            self.show_popup("You are missing details.")
        elif RegisterPage.check_email_validity(self, email) == False:
            self.show_popup("Your email is invalid!")
        elif RegisterPage.check_email(self, email) == False:
            self.show_popup("Your email domain is invalid!")
        else:
            cursor = mydb.cursor()
            query = "SELECT * FROM `university-review`.User WHERE username=%s OR email=%s"
            cursor.execute(query, (username, email))
            results = cursor.fetchall()
            print(results)
            if results:
                print("Username or email is already taken.")
            else:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                insertquery = "INSERT INTO `university-review`.`User` (`username`, `password`, `email`) VALUES (%s, %s, %s)"
                cursor.execute(insertquery, (username, hashed, email))
                mydb.commit()
                self.ids.username_ti.text = ""
                self.ids.password_ti.text = ""
                self.ids.email_ti.text = ""

    def show_popup(self, message):
        show = P()
        popupWindow = Popup(title="Error!", content=Label(text=message), size_hint=(None, None), size=(300, 150))
        popupWindow.open()  # show the popup

    def check_email_validity(self, email):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if(re.search(regex, email)):
            return True
        else:
            return False

    def check_email(self, email):
        domain = email.split('@')[1]
        cursor = mydb.cursor()
        query = "SELECT * FROM `university-review`.ValidEmail WHERE suffix=%s"
        cursor.execute(query, (domain,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False

class MainPage(Screen):
    def print_username(self):
        test = LoginPage()
        print(test.stored_username)

class WindowManager(ScreenManager):
    pass

if __name__=="__main__":
    main_app = SigninApp()
    main_app.run()
