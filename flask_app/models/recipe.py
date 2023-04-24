from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user # import user because of the relationship with the recipes table in db
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash

class Recipe:
    db = "recipe_share"
    def __init__(self,data):
        self.id = data['id']
        self.name = data['name']
        self.under_30 = data['under_30']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_cooked = data['date_cooked']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        # set to none for now - read class associations for this
        self.owner = None # set an owner when its created

    @classmethod
    def get_all(cls):
        # join is needed to get combined information from both the recipe
        # and the corresponding user in the users table
        query = """
                SELECT * FROM recipes
                JOIN users on recipes.user_id = users.id;
        """
        results = connectToMySQL(cls.db).query_db(query)
        recipes = []
        for recipe in results:
            this_recipe = cls(recipe)
            #build the user data because it's going to be stored in our recipe.owner object
            user_data = {
                "id": recipe['user_id'],
                "first_name": recipe['first_name'],
                "last_name": recipe['last_name'],
                "email": recipe['email'],
                "password": "", #except the password, unsafe to store but so we just leave it blank to keep our data structure
                "created_at": recipe['created_at'],
                "updated_at": recipe['updated_at'],
            }
            #when this_recipe was created, it's owner key was empty
            #so now we are passing the user's info who created this recipe 
            this_recipe.owner = user.User(user_data)
            # store all the now-combined data (recipe and user) inside of a list accesible from outside our for loop
            recipes.append(this_recipe)
        return recipes
    
    @classmethod
    def get_recipe_by_id(cls,data):
        query = """
                SELECT * FROM recipes
                JOIN users on recipes.user_id = users.id
                WHERE recipes.id = %(id)s;
        """
        result = connectToMySQL(cls.db).query_db(query,data)
        # stop if no matching recipe id
        if not result:
            return False
        result = result[0]
        this_recipe = cls(result)
        # a recipe belongs to just one user, so no need for a for loop
        user_data = {
                "id": result['users.id'],
                "first_name": result['first_name'],
                "last_name": result['last_name'],
                "email": result['email'],
                "password": "",
                "created_at": result['users.created_at'],
                "updated_at": result['users.updated_at']
        }
        this_recipe.creator = user.User(user_data)
        return this_recipe
    
    @classmethod
    def add_recipe(cls,data):
        query = """
                INSERT INTO recipes (name,under_30,description,instructions,date_cooked,user_id)
                VALUES (%(name)s,%(under_30)s,%(description)s,%(instructions)s,%(date_cooked)s,%(user_id)s)
                """
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def edit_recipe(cls,data):
        query = """
                UPDATE recipes
                SET name = %(name)s,
                under_30 = %(under_30)s,
                description = %(description)s,
                instructions = %(instructions)s,
                date_cooked = %(date_cooked)s
                WHERE id = %(id)s;
                """
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def delete_recipe(cls,data):
        query = """
                DELETE FROM recipes
                WHERE id = %(id)s;
                """
        return connectToMySQL(cls.db).query_db(query,data)
    
    @staticmethod
    def validate_add_recipe(data):
        is_valid = True
        # query = "SELECT * FROM users WHERE email = %(email)s;"
        # results = connectToMySQL(User.db).query_db(query,user)
        # if len(results) >= 1:
        #     flash("Email unavailable. Please use a different email.","register")
        #     is_valid = False
        if len(data['name']) < 3:
            flash("Recipe name must be at least 3 characters","add_recipe")
            is_valid = False
        if len(data['description']) < 1:
            flash("Description cannot be blank","add_recipe")
            is_valid = False
        if len(data['instructions']) < 1:
            flash("Instructions cannot be blank","add_recipe")
            is_valid = False
        if "under_30" not in data:
            flash("Does your recipe take less than 30 minutes to finish?","add_recipe")
            is_valid = False
        # if user['password'] != user['confirm']:
        #     flash("Passwords don't match.","add_recipe")
        #     is_valid = False
        return is_valid
    
