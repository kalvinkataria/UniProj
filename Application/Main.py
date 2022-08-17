import datetime
import kivy
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivymd.uix.menu import MDDropdownMenu
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.dialog import MDInputDialog, MDDialog
from kivymd.theming import ThemeManager
from kivymd.uix.snackbar import Snackbar
import mysql.connector
import socket_client
import bcrypt
import re

kivy.require("1.10.1")

# Logo
class Logo_white(FloatLayout):
    pass


class Logo_red(FloatLayout):
    pass


# Titles class
class Title(FloatLayout):
    pass


class logo_home_button(ButtonBehavior, Image):
    pass


# Drop down for scores (add_comment_page).
class CustomDropDown(DropDown):
    pass


# Header bar
class Header_Bar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    title_text = StringProperty()

    def Home_Button(self):
        chat_app.screen_manager.current = 'Main'

    def Settings_Button(self):
        chat_app.screen_manager.current = 'Account'

    def Search_Page_Button(self):
        chat_app.screen_manager.current = 'Search'

    def startSearch(self):
        chat_app.Search_Results.fillPage(self.ids.search_field.text,"University", False)
        chat_app.screen_manager.current = 'Search_Results'

class Footer_bar(FloatLayout):
    pass

# Class for university search
class search_widget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def startSearch(self):
        chat_app.Search_Results.fillPage(self.ids.search_field.text,"University", False)
        chat_app.screen_manager.current = 'Search_Results'


# Widget to pull data from the DB - will be refactored later
class DB_Button(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Widget to open chat client
class Chat_Button(FloatLayout):
    ip = "127.0.0.1"
    port = 1234
    username = 'tester'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Try to open the prev details as read
        with open("prev_details.txt", "r") as f:
            d = f.read().split(",")
        #   prev_ip = d[0]
        #  prev_port = d[1]
        # prev_username = d[2]

    def join_button(self, instance):
        ip = self.ip
        port = self.port
        username = self.username
        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")
        Clock.schedule_once(self.connect, 1)

    # passes time, don't need but kivy wants it
    def connect(self, _):
        port = int(self.port)
        ip = self.ip
        username = self.username

        # if nothing works this will return
        if not socket_client.connect(ip, port, username, show_error):
            return

        chat_app.create_chat_page()
        chat_app.screen_manager.current = 'Chat'


# Widget to display the content on each page

class Main_Menu(GridLayout):
    opacity_hold = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fillButtons(self):
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        cursor = cnx.cursor()
        query = "SELECT * FROM Page WHERE pageID = %s OR pageParent = %s"  # Gets all data for your page and parents
        cursor.execute(query,(chat_app.LogIn_Page.user_useruni,chat_app.LogIn_Page.user_useruni,))
        pages = cursor.fetchall()
        cnx.close()

        main_menu_buttons = [PageSelector() for i in range(0, 9)]
        for x in range(0, 9):
            try:
                main_menu_buttons[x].pageID = pages[x][0]
                main_menu_buttons[x].buttonText = (pages[x][2])
                main_menu_buttons[x].pageType = pages[x][3]
                self.add_widget(main_menu_buttons[x])
            except:
                pass


class searchResultsPage(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fillPage(self, search, input, fromPage):
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        cursor = cnx.cursor()

        if not fromPage:  # if looking for a result from search page, where we don't need to find only parents
            query = "SELECT * FROM Page WHERE pageName LIKE %s AND pageType = %s LIMIT 15"
            cursor.execute(query, ("%" + str(search) + "%",input,))
        elif fromPage:  # if looking for a result from content page
            if chat_app.Content_page.pageParent is None:
                query = "SELECT * FROM Page WHERE pageType = %s AND pageParent = %s LIMIT 15"
                cursor.execute(query, (input,chat_app.Content_page.pageID,))
            else:
                query = "SELECT * FROM Page WHERE pageType = %s AND pageParent = %s LIMIT 15"
                cursor.execute(query, (input,chat_app.Content_page.pageParent,))

        results = cursor.fetchall()
        cnx.close()
        self.ids.results.clear_widgets()
        resultslist = [searchItem() for i in range(0, len(results))]
        vertHint = 0.85
        for x in range(0, len(results)):
            resultslist[x].resultText = results[x][2]
            resultslist[x].resultType = results[x][3]
            resultslist[x].pageID = results[x][0]
            resultslist[x].size_hint = (0.8, .1)
            resultslist[x].pos_hint = {'x': 0.08, 'y': vertHint}
            vertHint -= 0.12
            self.ids.results.add_widget(resultslist[x])


class searchItem(ButtonBehavior, BoxLayout):
    pageID = 0
    resultText = StringProperty("")
    resultType = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        chat_app.screen_manager.current = 'Content'
        chat_app.Content_page.setID(self.pageID)
        chat_app.Content_page.gather_values()


class PageSelector(ButtonBehavior, BoxLayout):
    opacity_hold = 1
    buttonText = StringProperty()
    pageID = 0
    pageType = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def changeText(self, text):
        self.buttonText = text

    def assignIcon(self):
        pass

    def on_press(self):
        chat_app.screen_manager.current = 'Content'
        chat_app.Content_page.setID(self.pageID)
        chat_app.Content_page.gather_values()


# Navigation bar animation and functionality
class Nav_Bar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Store the previous screens (for "back" button)
    list_of_prev_screens = []

    # Reduce the opacity of the text when the nav bar is opened

    # All the follows is for the nav bar, will need refactoring later

    # Animation for opening
    def mbutton_animation_closed(self, widget):
        animation = Animation(vertical_hint=0, duration=0.2)
        animation.start(widget)

    def mbutton_animation_open(self, widget):
        animation = Animation(vertical_hint=.1, duration=0.2)
        animation.start(widget)

    def sbutton_animation_open(self, widget):
        animation = Animation(opacity=1, duration=1.5)
        animation &= Animation(vertical_hint=.15, duration=0.3)
        animation.start(widget)

    def fbutton_animation_open(self, widget):
        animation = Animation(opacity=1, duration=1.5)
        animation &= Animation(vertical_hint=.15, duration=0.3)
        animation &= Animation(horizontal_hint=.0, duration=0.3)
        animation.start(widget)

    def cbutton_animation_open(self, widget):
        animation = Animation(opacity=1, duration=1.5)
        animation &= Animation(vertical_hint=.15, duration=0.3)
        animation &= Animation(horizontal_hint=.2, duration=0.3)
        animation.start(widget)

    def tbutton_animation_open(self, widget):
        animation = Animation(opacity=1, duration=1.5)
        animation &= Animation(vertical_hint=.15, duration=0.3)
        animation &= Animation(horizontal_hint=.6, duration=0.3)
        animation.start(widget)

    def ubutton_animation_open(self, widget):
        animation = Animation(opacity=1, duration=2)
        animation &= Animation(vertical_hint=.15, duration=0.3)
        animation &= Animation(horizontal_hint=.8, duration=0.3)
        animation.start(widget)

    # Animation for closing the nav bar

    def mbutton_animation_reset(self, widget):
        animation = Animation(vertical_hint=.15, duration=0.1)
        animation.start(widget)

    def sbutton_animation_close(self, widget):
        animation = Animation(vertical_hint=0, duration=0.1)
        animation &= Animation(opacity=0)
        animation.start(widget)

    def fbutton_animation_close(self, widget):
        animation = Animation(horizontal_hint=.39, duration=0.1)
        animation &= Animation(opacity=0)
        animation &= Animation(vertical_hint=0, duration=0.1)
        animation.start(widget)

    def cbutton_animation_close(self, widget):
        animation = Animation(horizontal_hint=.39, duration=0.1)
        animation &= Animation(opacity=0)
        animation &= Animation(vertical_hint=0, duration=0.1)
        animation.start(widget)

    def tbutton_animation_close(self, widget):
        animation = Animation(horizontal_hint=.39, duration=0.1)
        animation &= Animation(opacity=0)
        animation &= Animation(vertical_hint=0, duration=0.1)
        animation.start(widget)

    def ubutton_animation_close(self, widget):
        animation = Animation(horizontal_hint=.39, duration=0.1)
        animation &= Animation(opacity=0)
        animation &= Animation(vertical_hint=0, duration=0.1)
        animation.start(widget)

    # Buttons to link to screen manager
    # These are called when button is pressed

    def toPage(self,pageType):
        chat_app.Content_page.toSubPage(pageType)


    def Back_button_stack(self):
        # Take the current page and add it to the list
        holder = chat_app.screen_manager.current

        self.list_of_prev_screens.append(holder)

        print(holder)  # <-- For debug

    def on_back_button(self):
        if self.list_of_prev_screens:
            # If there are then just go back to it
            chat_app.screen_manager.current = self.list_of_prev_screens.pop()
            # We don't want to close app
            return True
            # No more screens so user must want to exit app
        return False


# Pages

class First_Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def Login_Button(self):
        chat_app.screen_manager.current = 'Login'



class LogInPage(FloatLayout):
    user_username = ""   # Change for the chat client
    user_email = ""
    user_userID = 0
    user_useruni = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def login_button(self, username, password):
        # Database connection.
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        # Check if text inputs are not empty.
        if username == "" or password == "":
            self.show_popup("You are missing details.")
        else:
            cursor = cnx.cursor(buffered=True, dictionary=True)
            hashquery = "SELECT password FROM `university-review`.User WHERE username=%s"
            cursor.execute(hashquery, (username,))
            result = cursor.fetchall()
            if result:
                for x in result:
                    hashedpass = (x['password'])
                if bcrypt.checkpw(password.encode('utf-8'), hashedpass.encode('utf-8')):
                    hashquery = "SELECT userID, email from `university-review`.User WHERE username=%s"
                    cursor.execute(hashquery, (username,))
                    result = cursor.fetchall()
                    for x in result:
                        email = (x['email'])
                        userID = (x['userID'])
                    self.user_username = username
                    self.user_email = email
                    self.user_userID = userID
                    # store the user's uni as a string
                    domain = self.user_email.split('@')[1]
                    query = "SELECT Page.pageID FROM Page INNER JOIN ValidEmail ON Page.pageID = ValidEmail.uniID WHERE suffix = %s;"
                    cursor.execute(query, (domain,))
                    self.user_useruni = cursor.fetchall()[0].get("pageID")
                    cnx.close()

                    self.ids.username_field.text = ""
                    self.ids.pwd_field.text = ""
                    chat_app.screen_manager.current = 'Main'
                    chat_app.mainMenu.fillButtons()
                else:
                    self.show_popup("Your username or password is wrong!")
            else:
                self.show_popup("Your username or password is wrong!")

    # Show a popup message on screen.
    def show_popup(self, message):
        popupWindow = Popup(title="Error!", content=Label(text=message), size_hint=(None, None), size=(300, 150))
        popupWindow.open()  # show the popup


class SignUpPage(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def signup_button(self, username, email, password):
        # Database connection
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        if username == "" or email == "" or password == "":
            LogInPage.show_popup(self, "You are missing details.")
        elif not SignUpPage.check_email_validity(self, email):
            LogInPage.show_popup(self, "Your email is invalid!")
        elif not SignUpPage.check_email(self, email):
            LogInPage.show_popup(self, "Your email domain is invalid!")
        else:
            cursor = cnx.cursor(buffered=True, dictionary=True)
            query = "SELECT * FROM `university-review`.User WHERE username=%s OR email=%s"
            cursor.execute(query, (username, email))
            results = cursor.fetchall()
            if results:
                LogInPage.show_popup(self, "Username or email is already taken.")
            else:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                insertquery = "INSERT INTO `university-review`.`User` (`username`, `password`, `email`) VALUES (%s, " \
                              "%s, %s) "
                cursor.execute(insertquery, (username, hashed, email))
                cnx.commit()
                cnx.close()
                self.ids.username_field.text = ""
                self.ids.pwd_field.text = ""
                self.ids.email_field.text = ""
                LogInPage.show_popup(self, "You have successfully registered!")

    # Checks email validity to ensure it meets format.
    def check_email_validity(self, email):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regex, email):
            return True
        else:
            return False

    # Checks whether email in the database exists.
    def check_email(self, email):
        # Database connection
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        domain = email.split('@')[1]
        cursor = cnx.cursor()
        query = "SELECT * FROM `university-review`.ValidEmail WHERE suffix=%s"
        cursor.execute(query, (domain,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False


class MainPage(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Search_Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Content_page(FloatLayout):
    pageID = 1
    pageTitle = StringProperty("")
    pageDescription = StringProperty("")
    pageParent = 0
    pageImage = StringProperty("")
    pageScore = StringProperty("")
    labelHint = 0.3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setID(self, newID):  # gets the page ID
        self.pageID = newID

    def gather_values(self):  # gets the variables together required to fill the page
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        cursor = cnx.cursor()
        query = "SELECT * FROM Page WHERE pageID = %s"
        cursor.execute(query, (self.pageID,))
        details = cursor.fetchall()
        self.pageID = details[0][0]
        self.pageParent = details[0][1]
        self.pageTitle = details[0][2]
        self.pageDescription = details[0][4]

        # collect score
        query = "SELECT * FROM Comment WHERE pageID = %s"
        cursor.execute(query, (self.pageID,))
        details = cursor.fetchall()
        scores = 0
        count = 0
        for review in details:
            scores += details[count][4]
            count += 1
        if count < 1:
            count = 1
        scores /= count
        self.pageScore = str(round(scores))
        cnx.close()

    def toReviews(self):
        chat_app.Review_Page.fillPage()
        chat_app.screen_manager.current = 'Reviews'

    def toCompare(self):
        popupWindow = Popup(title="", content=Label(text="Please do this charles i am begging you"), size_hint=(None, None), size=(300, 150))
        popupWindow.open()  # show the popup

    def toSubPage(self,type):
        if self.pageParent is None:
            chat_app.Search_Results.fillPage("", type, True)
            chat_app.screen_manager.current = 'Search_Results'
        else:
            chat_app.Search_Results.fillPage("", type, False)
            chat_app.screen_manager.current = 'Search_Results'

class PageReview(FloatLayout):
    commentText = StringProperty("")
    commentDate = StringProperty("")
    commentScore = StringProperty("")
    commentVotes = StringProperty("")
    commentUsername = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    commentID = 0
    voted = 0

    def vote(self, value):
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')
        cursor = cnx.cursor()
        query = "SELECT EXISTS(SELECT * FROM VoteLog WHERE userID = %s AND commentID = %s)"
        cursor.execute(query, (chat_app.LogIn_Page.user_userID, self.commentID))
        result = cursor.fetchall()
        if result[0][0] == 0:
            query = "UPDATE Comment SET votes = votes + %s  WHERE commentID = %s"
            cursor.execute(query, (value, self.commentID))
            cnx.commit()
            query = "INSERT INTO VoteLog(userID, commentID, votescore) VALUES (%s,%s,%s)"
            cursor.execute(query, (chat_app.LogIn_Page.user_userID, self.commentID, value))
            cnx.commit()

        elif result[0][0] == 1:
            query = "SELECT votescore FROM VoteLog WHERE userID = %s AND commentID = %s"
            cursor.execute(query, (chat_app.LogIn_Page.user_userID, self.commentID,))
            result = cursor.fetchall()
            if result[0][0] == value:  # if you're trying to vote the same value twice
                query = "UPDATE Comment SET votes = votes - %s WHERE commentID = %s"  # subtract that value back
                cursor.execute(query, (value, self.commentID))
                cnx.commit()
                query = "DELETE FROM VoteLog WHERE userID = %s AND commentID = %s"  # revert vote in the votelog
                cursor.execute(query, (chat_app.LogIn_Page.user_userID, self.commentID,))
                cnx.commit()

            else:  # if it's an opposite vote
                query = "UPDATE Comment SET votes = votes + %s * 2 WHERE commentID = %s"  # we need to double the vote to "flip" it back
                cursor.execute(query, (value, self.commentID,))
                cnx.commit()
                query = "UPDATE VoteLog SET votescore = %s WHERE userID = %s AND commentID = %s"
                cursor.execute(query, (value, chat_app.LogIn_Page.user_userID, self.commentID,))
                cnx.commit()

            Snackbar(text="Your vote has been cast!").show()

        cnx.close()


# Uni review comments page
# REVIEW FORMAT - ID, PAGEID, CONTENT, POSTED TIME, SCORE, VOTES, USER
class Review_page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    opacity_hold = 1

    def getID(self):
        return chat_app.Content_page.pageID

    def get_comments(self):
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')
        cursor = cnx.cursor()
        query = "SELECT Comment.*, User.username FROM Comment INNER JOIN User ON User.userID = Comment.user WHERE pageID = %s ORDER BY Comment.votes DESC"
        cursor.execute(query, (self.getID(),))
        result = cursor.fetchall()

        cnx.close()

        return result

    def fillPage(self):
        self.ids.reviewcontent.clear_widgets()
        results = self.get_comments()
        comments = [PageReview() for i in range(0, len(results))]
        for x in range(0, len(comments)):
            comments[x].commentID = results[x][0]
            comments[x].commentText = results[x][2]
            comments[x].commentDate = str(results[x][3])
            comments[x].commentScore = str(results[x][4])
            comments[x].commentVotes = str(results[x][5])
            comments[x].commentUsername = str(results[x][7])
            self.ids.reviewcontent.add_widget(comments[x])


# text, date, score, votes, username
class Add_Comment_Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getID(self):
        return chat_app.Content_page.pageID

    def getUsername(self):
        return chat_app.LogIn_Page.user_userID

    def add_comment_button(self, input_comment,input_score):
        # Database connection
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        cursor = cnx.cursor()

        if input_comment == "":
            LogInPage.show_popup(self, "Your review appears to have no content. Please write a review to submit.")

        elif not input_score.isdecimal():
            LogInPage.show_popup(self, "Your score appears to be invalid. Please enter a score between 1/100.")

        elif input_score.isdecimal() and int(input_score) < 1 or int(input_score) > 100:
            LogInPage.show_popup(self, "Your score appears to be invalid. Please enter a score between 1/100.")

        else:
            allowedToPost = True
            # check if the user should be allowed to make this comment
            query = "SELECT pageParent FROM Page WHERE pageID = %s"  # check if we're on a page with a parent - we'll need to go up a level if so
            cursor.execute(query, (chat_app.Content_page.pageID,))
            parent = cursor.fetchall()[0][0]
            if parent is None:  # if there is no parent, we are on a uni page
                if chat_app.Content_page.pageID != chat_app.LogIn_Page.user_useruni:
                    allowedToPost = False
                    LogInPage.show_popup(self, "It doesn't look like you are from this university.")
            else:
                if parent != chat_app.LogIn_Page.user_useruni:
                    allowedToPost = False
                    LogInPage.show_popup(self, "It doesn't look like you are from this university.")

            if allowedToPost:
                content = input_comment
                posted = datetime.datetime.now()
                # Commit the data
                score = int(input_score)
                addcommentquery = "INSERT INTO Comment (PageID,content,posted,score,votes,user) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(addcommentquery, (self.getID(), content, posted, score, 0, self.getUsername()))
                cnx.commit()
                cnx.close()
                chat_app.Review_Page.fillPage()
                chat_app.screen_manager.current = 'Reviews'


class Account_Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change_details(self, current_username, current_password, new_username, new_password):
        changepassword = False
        changeusername = False
        # Check if current account details are filled out.
        if current_username == "" or current_password == "":
            LogInPage.show_popup(self, "Please enter current details!")
        # Check if new username and new password is empty.
        elif new_username == "" and new_password == "":
            LogInPage.show_popup(self, "Please enter something to change!")
        # Check if both username and password want to be changed.
        elif new_username != "" and new_password != "":
            if self.change_user_and_pass(current_username, current_password, new_username, new_password):
                LogInPage.show_popup(self, "You have changed your username and password!")
        # Check if password wants to be changed only.
        elif new_username == "":
            changepassword = True
            if changepassword:
                if self.change_password(current_username, current_password, new_password):
                    LogInPage.show_popup(self, "You have changed your password!")
        # Check if username wants to be changed only.
        elif new_password == "":
            changeusername = True
            if changeusername:
                if self.change_username(current_username, current_password, new_username):
                    LogInPage.show_popup(self, "You have changed your username!")

    # Change current username.
    def change_username(self, current_username, current_password, new_username):
        # Database connection.
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        changed = False
        # Checks whether new username exists already.
        if self.check_username_exists(new_username):
            LogInPage.show_popup(self, "New username already exists!")
        else:
            cursor = cnx.cursor(buffered=True, dictionary=True)
            passquery = "SELECT password FROM `university-review`.User WHERE username=%s"
            cursor.execute(passquery, (current_username,))
            result = cursor.fetchall()
            # Obtains password from current username entered.
            if result:
                for x in result:
                    hashedpass = (x['password'])
                # Check whether current password field matches password stored.
                if bcrypt.checkpw(current_password.encode('utf-8'), hashedpass.encode('utf-8')):
                    query = "UPDATE `university-review`.`User` SET `username` = %s WHERE `username` = %s"
                    cursor.execute(query, (new_username, current_username))
                    cnx.commit()
                    cnx.close()
                    self.ids.current_username_field.text = ""
                    self.ids.current_pwd_field.text = ""
                    self.ids.new_username_field.text = ""
                    self.ids.new_pwd_field.text = ""
                    changed = True
                    return changed
                else:
                    LogInPage.show_popup(self, "Current pass doesn't match stored pass.")
            else:
                LogInPage.show_popup(self, "Your current username is wrong!")

    # Change current password.
    def change_password(self, current_username, current_password, new_password):
        # Database connection.
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        changed = False
        # Checks whether username exists in database.
        if self.check_username_exists(current_username):
            cursor = cnx.cursor(buffered=True, dictionary=True)
            passquery = "SELECT password FROM `university-review`.User WHERE username=%s"
            cursor.execute(passquery, (current_username,))
            result = cursor.fetchall()
            # Obtains password from current username entered.
            if result:
                for x in result:
                    hashedpass = (x['password'])
                # Check whether current password field matches password stored.
                if bcrypt.checkpw(current_password.encode('utf-8'), hashedpass.encode('utf-8')):
                    query = "UPDATE `university-review`.`User` SET `password` = %s WHERE `username` = %s"
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute(query, (hashed_new_password, current_username))
                    cnx.commit()
                    cnx.close()
                    self.ids.current_username_field.text = ""
                    self.ids.current_pwd_field.text = ""
                    self.ids.new_username_field.text = ""
                    self.ids.new_pwd_field.text = ""
                    changed = True
                    return changed
                else:
                    LogInPage.show_popup(self, "Current pass doesn't match stored pass?")
            else:
                LogInPage.show_popup(self, "Your current username is wrong!")
        else:
            LogInPage.show_popup(self, "Current username doesn't exist.")

    def change_user_and_pass(self, current_username, current_password, new_username, new_password):
        # Database connection
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        changed = False
        # Checks whether username exists in database.
        if self.check_username_exists(current_username):
            cursor = cnx.cursor(buffered=True, dictionary=True)
            passquery = "SELECT password FROM `university-review`.User WHERE username=%s"
            cursor.execute(passquery, (current_username,))
            result = cursor.fetchall()
            # Obtains password from current username entered.
            if result:
                for x in result:
                    hashedpass = (x['password'])
                # Check whether current password field matches password stored.
                if bcrypt.checkpw(current_password.encode('utf-8'), hashedpass.encode('utf-8')):
                    query = "UPDATE `university-review`.`User` SET `username` = %s, `password` = %s WHERE `username` = %s"
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute(query, (new_username, hashed_new_password, current_username))
                    cnx.commit()
                    cnx.close()
                    self.ids.current_username_field.text = ""
                    self.ids.current_pwd_field.text = ""
                    self.ids.new_username_field.text = ""
                    self.ids.new_pwd_field.text = ""
                    changed = True
                    return changed
                else:
                    LogInPage.show_popup(self, "Current pass doesn't match stored pass!")
            else:
                LogInPage.show_popup(self, "Your current username is wrong!")
        else:
            LogInPage.show_popup(self, "Current username doesn't exist!")

    def check_username_exists(self, username):
        # Database connection
        cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                                      host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                                      database='university-review')

        cursor = cnx.cursor()
        query = "SELECT * FROM `university-review`.User WHERE username=%s"
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        cnx.close()
        if results:
            return True
        else:
            return False


class Settings_Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# This class is an improved version of Label
# Kivy does not provide scrollable label, so we need to create one
class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ScrollView does not allow us to add more than one widget, so we need to trick it
        # by creating a layout and placing two widgets inside it
        # Layout is going to have one column and and size_hint_y set to None,
        # so height won't default to any size (we are going to set it on our own)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        # Now we need two widgets - Label for chat history and 'artificial' widget below
        # so we can scroll to it every new message and keep new messages visible
        # We want to enable markup, so we can set colors for example
        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()

        # We add them to our layout
        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    # Methods called externally to add new message to the chat history
    # Add a chat history ID here
    # May need to create a new method here for the global history ?
    def update_chat_history(self, message):
        # First add new line and message itself
        self.chat_history.text += '\n' + message

        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at teh bottom)
        # Set chat history label to whatever height of chat history text is
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

        # As we are updating above, text height, so also label and layout height are going to be bigger
        # than the area we have for this widget. ScrollView is going to add a scroll, but won't
        # scroll to the botton, nor there is a method that can do that.
        # That's why we want additional, empty wodget below whole text - just to be able to scroll to it,
        # so scroll to the bottom of the layout
        self.scroll_to(self.scroll_to_point)

    def update_chat_history_layout(self, _=None):
        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at the bottom)
        # Set chat history label to whatever height of chat history text is
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)


class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # We are going to use 1 column and 2 rows
        self.cols = 1
        self.rows = 2

        # First row is going to be occupied by our scrollable label
        # We want it be take 90% of app height
        self.history = ScrollableLabel(height=Window.size[1] * 0.9, size_hint_y=None)
        self.add_widget(self.history)

        # In the second row, we want to have input fields and Send button
        # Input field should take 80% of window width
        # We also want to bind button click to send_message method
        self.new_message = TextInput(width=Window.size[0] * 0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Send")
        self.send.bind(on_press=self.send_message)

        # To be able to add 2 widgets into a layout with just one collumn, we use additional layout,
        # add widgets there, then add this layout to main layout as second row
        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)

        # To be able to send message on Enter key, we want to listen to keypresses
        Window.bind(on_key_down=self.on_key_down)

        Clock.schedule_once(self.focus_text_input, 1)

        socket_client.start_listening(self.incoming_message, show_error)

        self.bind(size=self.adjust_fields)

    # Get the time stamp for the messages
    def get_time_stamp(self):
        return datetime.datetime.now()

    # Gets called on key press
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):

        # But we want to take an action only when Enter key is being pressed, and send a message
        if keycode == 40:
            self.send_message(None)

    # Gets called when either Send button or Enter key is being pressed
    # (kivy passes button object here as well, but we don;t care about it)
    def send_message(self, _):

        # Get message text and clear message input field
        message = self.new_message.text
        self.new_message.text = ''

        # If there is any message - add it to chat history and send to the server
        if message:
            # Our messages - use red color for the name
            time_stamp = self.get_time_stamp()
            username = "test"
            self.history.update_chat_history(f'[color=dd2020]{username}:  {message}  -  {time_stamp}[/color] >')
            socket_client.send(message)

        # As mentioned above, we have to schedule for refocusing to input field
        Clock.schedule_once(self.focus_text_input, 0.1)

    # Sets focus to text input field
    def focus_text_input(self, _):
        self.new_message.focus = True

    # Passed to sockets client, get's called on new message
    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username

        self.history.update_chat_history(f'[color=20dd20]{username}: {message}[/color] >')

        # Updates page layout

    def adjust_fields(self, *_):

        # Chat history height - 90%, but at least 50px for bottom new message/send button part
        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.9
        self.history.height = new_height

        # New message input width - 80%, but at least 160px for send button
        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width

        # Update chat history layout
        # self.history.update_chat_history_layout()
        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)


# "Main" Class
class UniApp(MDApp):
    opacity_hold = 1  # working on this
    cnx = ""
    cursor = ""
    currentPage = ""
    Window.size = (480, 853)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        theme_cls = ThemeManager()
        # We are going to use screen manager, so we can add multiple screens
        # and switch between them
        self.screen_manager = ScreenManager()

        def onBackBtn(self, window, key, *args):
            """ To be called whenever user presses Back/Esc key """
            # 27 is back press number code
            if key == 27:
                # Call the "OnBackBtn" method from the "ExampleRoot" instance
                return self.root.onBackBtn()
            return False

        # Initial, connection screen (we use passed in name to activate screen)
        # First create a page, then a new screen, add page to screen and screen to screen manager

        # First Page
        self.First_Page = First_Page()
        screen = Screen(name='First')
        screen.add_widget(self.First_Page)
        self.screen_manager.add_widget(screen)

        # Login Page
        self.LogIn_Page = LogInPage()
        screen = Screen(name='Login')
        screen.add_widget(self.LogIn_Page)
        self.screen_manager.add_widget(screen)

        # Sign Up page
        self.SignUp_Page = SignUpPage()
        screen = Screen(name='SignUp')
        screen.add_widget(self.SignUp_Page)
        self.screen_manager.add_widget(screen)

        # Main Page
        self.main_page = MainPage()
        screen = Screen(name='Main')
        screen.add_widget(self.main_page)
        self.screen_manager.add_widget(screen)

        # Creating a main menu instance
        self.mainMenu = Main_Menu()
        self.main_page.add_widget(self.mainMenu)

        # Search Page
        self.Search_Page = Search_Page()
        screen = Screen(name='Search')
        screen.add_widget(self.Search_Page)
        self.screen_manager.add_widget(screen)

        # Facility Page
        self.Content_page = Content_page()
        screen = Screen(name='Content')
        screen.add_widget(self.Content_page)
        self.screen_manager.add_widget(screen)

        # Accounts Page
        self.Account_Page = Account_Page()
        screen = Screen(name='Account')
        screen.add_widget(self.Account_Page)
        self.screen_manager.add_widget(screen)

        # Chat_Button
        self.Chat_Button = Chat_Button()
        screen = Screen(name='Chat_Button')
        screen.add_widget(self.Chat_Button)
        self.screen_manager.add_widget(screen)

        # Comments page
        self.Review_Page = Review_page()
        screen = Screen(name='Reviews')
        screen.add_widget(self.Review_Page)
        self.screen_manager.add_widget(screen)

        # Search results page
        self.Search_Results = searchResultsPage()
        screen = Screen(name='Search_Results')
        screen.add_widget(self.Search_Results)
        self.screen_manager.add_widget(screen)

        # Add comment page
        self.Add_Comment = Add_Comment_Page()
        screen = Screen(name='Add_Comment')
        screen.add_widget(self.Add_Comment)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    # We cannot create chat screen with other screens, as its init method will start listening
    # for incoming connections, but at this stage connection is not being made yet, so we
    # call this method later
    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name='Chat')
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)

    def set_previous_screen(self):
        self.sm.current = self.sm.previous()

    def reduce_text_opacity(self):
        self.opacity_hold = 0.2

    def on_start(self):
        pass

    def option_callback(self, input):
        Add_Comment_Page.score = input


# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
# time.sleep() won't work here - will block Kivy and page with error message won't show up
def show_error(message):
    print("error")
    # chat_app.info_page.update_info(message)
    # chat_app.screen_manager.current = 'Info'
    # Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = UniApp()
    chat_app.run()
