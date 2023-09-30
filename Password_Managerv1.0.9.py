# Modules
import kivy   # This is the GUI module
import sqlite3 as sql   # Database module

# Classes specific to Kivy module
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import NoTransition
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.config import Config

# This will load the GUI instructions write from the other file.
Builder.load_file('mainv1.0.6.kv')


class PopupBox(Popup):
    """This class is for the popup."""
    pass


class PasswordInfoRetainer(FloatLayout):
    """Password info retainer is the widget which will store the password
    along with the platform and username associated with it and display it.
    """

    def __init__(self,
                 recordId,
                 platformName,
                 username,
                 password,
                 userId,
                 parent_widget,
                 **kwargs):
        super().__init__(**kwargs)

        # Stores information unique to this object/widget
        self.userId = userId
        self.recordId = recordId
        self.platformName = platformName
        self.username = username
        self.password = password

        self.create_widget(parent_widget)

    def create_widget(self, parent):
        """Create the widget Password Info Retainer when called."""

        # Set the Password info retainer to display it's given information
        self.ids.platformName.text = self.platformName
        self.ids.username.text = self.username
        self.ids.passwordName.text = self.password

        # Attach to the scrollbar in password manager menu
        parent.add_widget(self)

    def remove_record(self):
        """When the user wants to remove a username and password set saved
        to their password this will execute, removing it from
        stored_password_information table and data base (data_base.db).
        """

        # Opens the data_base.db file.
        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # Sql query to remove username and password set from the
        # stored_password_information table and data base (data_base.db).
        removeSavedPassword = """DELETE FROM stored_password_information
                                WHERE primary_key = ?
                                and platform = ?
                                and username = ?
                                and password = ?
                                and parent_user_id = ?
                                """

        # Executes the sql query.
        cursor.execute(removeSavedPassword,
                       [self.recordId,
                        self.platformName,
                        self.username,
                        self.password,
                        self.userId])

        # Saves change to data base.
        dataBaseConnection.commit()

        # Removes info widget from password manager menu
        self.parent.remove_widget(self)

    def edit_record(self):
        """Will open the edit window and load the data
           stored inside the intended widget to be edited.
            """

        # Gets the root object of the app
        root = App.get_running_app().root

        # Accesses the edit window page and sets
        # it's editing target to the intended widget.
        root.screens[5].recordObject = self

        # Sets the background text of the input box
        # to the stored existing info.
        root.screens[5].ids.platformInput.hint_text = self.platformName
        root.screens[5].ids.usernameInput.hint_text = self.username
        root.screens[5].ids.passwordInput.hint_text = self.password

        # Sets the text inside of the input boxes in
        # the edit window to display the existing info.
        root.screens[5].ids.platformInput.text = self.platformName
        root.screens[5].ids.usernameInput.text = self.username
        root.screens[5].ids.passwordInput.text = self.password

        # Change the page to the edit window.
        root.current = "Edit window"


# Home page.
class HomePage(Screen):
    """This is the first page people will see when they open the app."""

    pass


# Login page.
class LoginPage(Screen):
    """Login page is the page where people will log into their accounts."""

    def login(self):
        """This will check the user's input, try to match it to the
        data base and log them into their account if it matches.
        """

        username = self.ids.username.text
        password = self.ids.password.text

        # Creates a SQL query to search the data base
        # for matching username and password.
        login = "SELECT * FROM user WHERE username = ? and password = ?"

        # Return a table with of rows wtih matching username and password.
        cursor.execute(login, [username, password])

        # Get the first instance
        matchingAccount = cursor.fetchone()

        # Checks the username and password to see if
        # there are any problems with it.
        error = PasswordManager.username_password_check(self,
                                                        username,
                                                        password)

        # This if statement is only really here as
        # to avoid multiple errors popuping up at once.
        if error is True:
            return
        elif matchingAccount is None:
            # No matching username and password could
            # be found give the User an error.

            PasswordManager.create_popup(self, "Errror", "Wrong " +
                                         "username or password entered!")
            error = True

        elif matchingAccount is not None and error is False:
            # If the account exist and the username and password match
            # and there are no issues wtih the User's input for
            # username and password then log them in.

            # Set the Password manager menu's userId to the logged in User's id
            self.manager.screens[4].userId = matchingAccount[0]

            # Load in the the User's stored passwords.
            self.manager.screens[4].load_existing_record()

            # Change page
            App.get_running_app().change_page(self, "Password manager menu")


# Sign up page
class SignupPage(Screen):
    """Signup page is where people will create new
    accounts so they can manger their passwords.
    """

    def create_account(self):
        """When this function is fired when the use attempts to make their account it
            will check for errors with the user's input but if
            there aren't any problems found with it will allow the
            account to be made.
            """

        # Get the input in the input boxes from the user.
        username = self.ids.username.text
        password = self.ids.password.text
        confirmPassword = self.ids.confirmPassword.text
        age = self.ids.age.text

        # Openings the SQL data base.
        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # Creates a querie for the SQL data base where it
        # ask if the username already exist.
        checkUsername = "SELECT * FROM user WHERE username = ?"

        # Executes the querie mentioned above in the SQL data base.
        cursor.execute(checkUsername, [username])

        # When the function has checked that all potential Errors with
        # the user's input have not occur will it then say there are no
        # errors with the user's input; Allowing the user to create an account.

        try:
            if password is "" \
             and username is "" \
             and confirmPassword is "" \
             and age is "":
                # If nothing was inputted then give
                # an error asking for user input.

                PasswordManager.create_popup(self, "ERROR", "You haven't " +
                                             "filled in anything! \nPlease " +
                                             "fill in the boxes to create " +
                                             "your account.")
            elif PasswordManager.username_password_check(self,
                                                         username,
                                                         password) is True:
                # This if statement branch here is only really here
                # as to not have multiple error messages popup but the
                # elif branch here checks the username and password for errors.

                return
            elif " " in confirmPassword:
                # If the user entered spacebars into the confirm password
                # input box then ask User to remove them.

                PasswordManager.create_popup(self, "ERROR", "Please remove " +
                                             "any spacebar(s) in the " +
                                             "confirm box.")

            elif confirmPassword is "":
                # If nothing was entered for confirm password then ask
                # them to enter their password again.

                PasswordManager.create_popup(self, "ERROR", "Please enter " +
                                             "in your password inside\n" +
                                             "confirm password box! "
                                             "it can't be empty.")

            elif cursor.fetchall():
                # Give an error popup to the user explaining the
                # username they want to use already exist.

                PasswordManager.create_popup(self, "ERROR", "Username has " +
                                             "already taken! Please use an " +
                                             "alternative username.")

            elif len(password.strip()) < 8:
                # IF the password length was shorter than 8 characters long
                # then ask them to make their password 8 characters long.

                PasswordManager.create_popup(self, "ERROR", "The password " +
                                             "must be 8 character long " +
                                             "or longer.")

            elif password != confirmPassword:
                # If the confirm password doesn't match the password
                # then tell them the passwords don't match.

                PasswordManager.create_popup(self, "ERROR", "The confirm " +
                                             "password does not match with " +
                                             "password!")
            elif int(age.strip()) <= 0:
                # if the age of the User is below 0 then tell
                # them to enter their actual age the program.

                PasswordManager.create_popup(self, "ERROR", "Please enter " +
                                             "your actual age!")
            elif int(age.strip()) < 13:
                # if the age of the User is below 13 then
                # tell them they can't use the program.

                PasswordManager.create_popup(self, "ERROR", "You are not " +
                                             "old enough to use this program.")
            else:
                # If all conditions for a error is not met
                # then there must not be any errors.

                # Create a SQL instruction to insert the username and password
                # of this new account into the data base.
                insertData = """INSERT INTO
                                 user(username, password)
                                 values(?,?)
                                 """

                # Execute the SQL instruction made.
                cursor.execute(insertData, [username, password])

                # Save the changes to the data base.
                dataBaseConnection.commit()

                # Create SQL query to find the new account.
                getAccount = """SELECT * FROM user
                            WHERE username = ? and password = ?
                            """

                # Get the table containing the new account.
                sqlTable = cursor.execute(getAccount,
                                          [username,
                                           password]).fetchall()

                # Get the new account's User id.
                userId = sqlTable[0][0]

                # Set the password manager menu to save
                # passwords according to this userId.
                self.manager.screens[4].userId = userId

                # Change page
                App.get_running_app().change_page(self,
                                                  "Password manager menu")

        except ValueError:
            # If the User failed to input a correct number then...

            if age is "":
                # User didn't enter anything then...
                # User age input was invalid.
                PasswordManager.create_popup(self, "ERROR",
                                             "Please enter in your age!")
            else:
                PasswordManager.create_popup(self, "ERROR", "Please enter " +
                                             "only FULL numbers I.E '5'" +
                                             "\nNO WORDS I.E 'FIVE'"
                                             "\nNO LETTERS I.E 'ABCDE'" +
                                             "\nNO SPECIAL CHARACTERS " +
                                             "I.E '!@#$%^&*'"
                                             "\nNO DECIMALS I.E '2.5'")


# Password manager menu screen, where Users can see their
# username and passwords stored for different accounts.
class PasswordManagerMenu(Screen):
    """Password manager menu is where people will
    be able to manager their passwords.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.userId = ""

    def load_existing_record(self):
        """When the Password manager menu is opened, it will load all of
        the username and passwords stored to the logged in account.
        """

        # Open data_base.db file.
        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # Sql query, Get all saved username and passwords
        # associated with logged in account.
        getSavedPasswords = """SELECT * FROM stored_password_information
                            WHERE parent_user_id = ?
                            """

        # Executes the sql query to find all username and passwords stored
        # to the logged in account (self.userId).
        cursor.execute(getSavedPasswords, [self.userId])

        # Saves returned data to a variable.
        passwordsList = cursor.fetchall()

        # For every username and password set saved in accountList
        # create a widget for it to display information.
        for passwordRecord in passwordsList:

            PasswordInfoRetainer(passwordRecord[0],
                                 passwordRecord[1],
                                 passwordRecord[2],
                                 passwordRecord[3],
                                 self.userId,
                                 self.ids.main)

    def logout(self):
        """Logs out of the User's account then removes all widgets of
        username and passwords stored from that account for that page to
        be used for when someone else logs in.
        """

        # Logs out of the current account logined in
        self.userId = ""

        # Collects the widgets for accounts current account.
        infoRetainers = self.ids.main.children

        # Removes all the collected widgets of
        # information of username and passwords.
        while len(infoRetainers) > 0:
            self.ids.main.remove_widget(infoRetainers[0])

        # Goes back to home page.
        self.manager.current = "Home page"

    def check_record_input(self):
        """Check if the input for the record is valid or not"""

        # This variable is a boolean which will
        # be return true or false if there are errors.
        isError = True

        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # create SQL query to check if this input matches
        # some already saved password record.
        checkDupes = """SELECT platform, username
                        FROM stored_password_information
                        WHERE parent_user_id = ?
                        AND platform = ?
                        AND username = ?
                        """

        # execute query to return row of platform and usernames which match.
        cursor.execute(checkDupes, [self.manager.screens[4].userId,
                                    self.ids.platformInput.text,
                                    self.ids.usernameInput.text])

        # Like the other input checking functions this one will also
        # first assume something is wrong with the input, else if
        # there is nothing found to be invalid isError returns False.
        if (self.ids.platformInput.text).strip() is "":
            # If the User entered nothing for platform

            PasswordManager.create_popup(self, "ERROR", "Please enter in " +
                                         "the name of the platform! It " +
                                         "can't be empty.")

        elif (self.ids.usernameInput.text).strip() is "" and \
             (self.ids.passwordInput.text).strip() is "":
            # If the User entered nothing for both username
            # and platform give them error.

            PasswordManager.create_popup(self, "ERROR", "Please enter in " +
                                         "either usename or password! One " +
                                         "can't be empty.")

        elif " " in self.ids.passwordInput.text:
            # If the user password has spacebars in password give them error.
            PasswordManager.create_popup(self, "ERROR", "You cannot have " +
                                         "spacebar(s) in your password! " +
                                         "Please remove them.")

        elif cursor.fetchall():
            # If the record the use wants to
            # add/change to exist give them error.
            PasswordManager.create_popup(self, "ERROR", "You have already" +
                                         " saved a password for this account!")

        else:
            # If no conditions could be met for invalid
            # input then input must be valid.

            isError = False

        return isError


# Add account window is when the user is saving another username and password
# to their account management tool account.
class AddPasswordWindow(Screen):
    """Add account window is where they will be inputting the
        details of their password for what platform and username.
        """

    def create_record(self):
        """Create an account info widget, these widgets save the
        username and password for an account they use for a platform.
        """

        # Check if the input for the record is valid.
        isError = PasswordManagerMenu.check_record_input(self)

        if isError is True:
            # If there is errors then stop the function from saving record.
            return

        # Gets the User Id of the account
        userId = self.manager.screens[4].userId

        # Opens the data_base.db file.
        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # Sql query to insert the platform, username and password and logged
        # in userid into stored_password_information table.
        saveAccountDetails = """INSERT INTO stored_password_information(
                                platform,
                                username,
                                password,
                                parent_user_id)
                                values(?,?,?,?)
                                """

        # Executes the written query above.
        cursor.execute(saveAccountDetails,
                       [self.ids.platformInput.text,
                        self.ids.usernameInput.text,
                        self.ids.passwordInput.text,
                        userId])

        # Saves entry into the table stored_password_information.
        # and database (data_base.db).
        dataBaseConnection.commit()

        # Create a task to find the heightest current record id.
        currentPrimaryKey = """SELECT primary_key
                               FROM stored_password_information
                               WHERE primary_key = (SELECT MAX(Primary_key)
                               FROM stored_password_information)
                               """

        # Save the highest record Id.
        recordId = cursor.execute(currentPrimaryKey).fetchone()[0]

        # Instancing (creating) an Account Info Widget.
        PasswordInfoRetainer(recordId,
                             self.ids.platformInput.text,
                             self.ids.usernameInput.text,
                             self.ids.passwordInput.text,
                             self.manager.screens[4].userId,
                             self.manager.screens[4].ids.main)

        # Change page
        App.get_running_app().change_page(self, "Password manager menu")


class EditWindow(Screen):
    """Edit window is where they can change their saved
    password records if any records have changed since then.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.recordObject = ""

    def save_edit(self):
        """This function is fired when the player is happy
        with the edits and clicks 'save edits' it will update
        the SQL database with the new details they have changed.
        """

        # Check if the edits to the records are valid.
        isError = PasswordManagerMenu.check_record_input(self)

        if isError is True:
            # If it is empty then stop the function
            # from changing the password info.
            return

        # retrieve the input from the user.
        platform = self.ids.platformInput.text
        username = self.ids.usernameInput.text
        password = self.ids.passwordInput.text

        # Set the text of the widget to display the new changes.
        self.recordObject.ids.platformName.text = platform
        self.recordObject.ids.username.text = username
        self.recordObject.ids.passwordName.text = password

        # saves information unique to this object/widget.
        self.recordObject.platformName = platform
        self.recordObject.username = username
        self.recordObject.password = password

        # Make a connection to the data base.
        with sql.connect('data_base') as dataBaseConnection:
            cursor = dataBaseConnection.cursor()

        # Create an instruction to update the data base.
        UpdateRecord = """UPDATE stored_password_information
                          SET platform = ?,
                          username = ?,
                          password= ?
                          WHERE primary_key = ?
                          """

        # Create update the data base with the changes given by user.
        cursor.execute(UpdateRecord,
                       [platform,
                        username,
                        password,
                        self.recordObject.recordId])

        # Save the changes to data base.
        dataBaseConnection.commit()

        # Remove the object from being edited.
        self.recordObject = ""

        # Change the page back to the password manager menu.
        self.manager.current = "Password manager menu"


# Core app
class PasswordManager(App):
    """This is the class which runs when the user opens the program."""

    def build(self):
        """This is what will create the UI of the program."""

        # Set the title.
        self.title = "Password manager"

        # Screenmanager is the class which creates branches.
        # between pages to switch between.
        self.sm = ScreenManager(transition=NoTransition())
        # Make it so there are no transitions when switching between pages.

        # Add these pages to the app to transition between.
        self.sm.add_widget(HomePage(name="Home page"))
        self.sm.add_widget(LoginPage(name="Login page"))
        self.sm.add_widget(SignupPage(name="Signup page"))
        self.sm.add_widget(AddPasswordWindow(name="Add password window"))
        self.sm.add_widget(PasswordManagerMenu(name="Password manager menu"))
        self.sm.add_widget(EditWindow(name="Edit window"))

        # Return this as the UI of the program.
        return self.sm

    def create_popup(self, title, context):
        """Create a popup window for the program."""

        # Instances a popup windo then sets the
        # popup's properties to passed parameters.
        popup = PopupBox()
        popup.title = title
        popup.ids.context.text = context

        # Show the popup to the user
        popup.open()

    def username_password_check(self, username, password):
        """This function will check the username and password textboxes."""

        # The function will first assume there is something wrong
        # with the username or password.
        errors = True

        # It will check the User's username
        # and password input for any errors.
        if " " in username:
            # If spacebars were found in the username
            # give them popup message to remove them.

            PasswordManager.create_popup(self, "ERROR", "Please remove the " +
                                         "spacebar(s) in your username.")
        elif " " in password:
            # If spacebars were entered give them an error
            # popup message to remove them.

            PasswordManager.create_popup(self, "ERROR", "Please remove the " +
                                         "spacebar(s) in your password.")
        elif username is "" and password is "":
            # Both username and password were empty then give them
            # an error popup to enter both.

            PasswordManager.create_popup(self, "ERROR", "Please enter in " +
                                         "your username and password!")
        elif username is "":
            # If no username was entered give them
            # an error popup message to enter one.

            PasswordManager.create_popup(self, "ERROR", "Please enter in a " +
                                         "username! It can't be empty.")
        elif password is "":
            # If no password was entered give them
            # an error popup message to enter one.

            PasswordManager.create_popup(self, "ERROR", "Please enter in a " +
                                         "password! It can't be empty.")
        else:
            # IF the conditions above aren't met then there is nothing wrong.

            errors = False

        # Return whether or not there are
        # any errors found in the username or input.
        return errors

    def clear_input_boxes(self):
        """Clears the input of a pages."""

        # Collects all the objects with ids attached
        # to them, usually input boxes will have ids.
        objects = self.ids.values()

        # For each object in this list of objects
        for object in objects:
            # if the object is a TextInput Widget
            if isinstance(object, TextInput):

                # clear the text inside of it.
                object.text = ""

    def change_page(self, page, targetPage):
        """This function is only for buttons
        that are on pages with input boxes.
        """

        PasswordManager.clear_input_boxes(page)

        page.manager.current = targetPage

    def exit(self):
        """Exits the program."""

        # Gets the running instance of the app.
        host = App.get_running_app()

        # Stops the app from running.
        host.stop()
        Window.close()


if __name__ == "__main__":
    # main routine.

    # create a connection to the database.
    dataBaseConnection = sql.connect("data_base")
    cursor = dataBaseConnection.cursor()

    # Create the table if it doesn't exist for password manager users.
    cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                    user_id INTEGER PRIMARY KEY,
                    username     TEXT NOT NULL,
                    password     TEXT NOT NULL);
                    """)

    # Create the table if it doesn't exist for
    # username and passwords stored to this app locally.
    cursor.execute("""CREATE TABLE IF NOT EXISTS stored_password_information(
                    primary_key INTEGER PRIMARY KEY,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    parent_user_id INTEGER NOT NULL,
                    FOREIGN KEY(parent_user_id) REFERENCES user(user_id));
                    """)
    # Save these changes.
    dataBaseConnection.commit()

    # Configurates the settings of the app.
    Config.set('graphics', 'width', 500)
    Config.set('graphics', 'height', 500)
    # Fix Window size to be 500 by 500.
    Config.set('graphics', 'resizable', 0)
    # Removes the red circles created when right clicking.
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.write()

    PasswordManager().run()
