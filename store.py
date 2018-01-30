from bottle import route, run, template, static_file, get, post, delete, request
from sys import argv
import json
import pymysql


@get("/admin")
def admin_portal():
	return template("pages/admin.html")

@get("/")
def index():
    return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico|jpeg)>')
def images(filename):
    return static_file(filename, root='images')

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Willyboy1@',
                             db='Store',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

#Get a category
@get('/categories')
def get_categories():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Categories"
            cursor.execute(sql)
            result = cursor.fetchall()
            print result
            return json.dumps({"STATUS": "SUCCESS", "CATEGORIES": result, "CODE": "200 - Success"})
    except:
        return json.dumps({"STATUS": "ERROR", "MSG": "Internal Error", "CODE": "500 - Internal error"})

#Get a product
@get('/products')
def get_products():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Products"
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({"STATUS": "SUCCESS", "PRODUCTS": result, "CODE": "200 - Success"})
    except:
        return json.dumps({"STATUS": "ERROR", "MSG": "Internal Error", "CODE": "500 - Internal error"})

#Function to get all categories
def getAllCategories():
    return_obj={}
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Categories"
            cursor.execute(sql)
            result = cursor.fetchall()
            #print result
            if len(result) == 0:
                print "if in categories"
                return {"STATUS": "ERROR", "CODE": "404 - Category not found"}
            else:
                return_obj["STATUS"]="SUCCESS"
                return_obj["CATEGORIES"]=result
                print return_obj
                print "else statement in categories"
                #return result
                return {"STATUS": "SUCCESS", "CATEGORIES": result, "CODE": "200 - Success"}
    except Exception as e:
        return_obj["STATUS"] = "SUCCESS"
        return_obj["MSG"] = "ERROR"
        return return_obj

#List products by category
@get('/category/<categoryID>/products')
def list_products_by_cat(categoryID):
    return_object={}
    all_categories=getAllCategories()
    print all_categories
    for item in all_categories["CATEGORIES"]:
        print item
        if item['id']==int(categoryID):
            try:
                with connection.cursor() as cursor:
                    sql="select * from PRODUCTS where category={}".format(int(categoryID))
                    cursor.execute(sql)
                    result=cursor.fetchall()
                    return_object["STATUS"]="Success"
                    return_object["PRODUCTS"]=result
                    print return_object
                    return json.dumps(return_object)
            except Exception as e:
                return_object["STATUS"]='ERROR'
                return_object["MSG"]=repr(e)
                print return_object
                return json.dumps(return_object)
    return_object["STATUS"]="ERROR"
    return_object["MSG"]="Internal error"
    return_object["CODE"]= "500 - internal error"
    return json.dumps(return_object)

#Getting a product
@get('/product/<categoryID>')
def getting_a_product(categoryID):
    all_categories=getAllCategories()
    print all_categories
    for item in all_categories["CATEGORIES"]:
        if item['id']==int(categoryID):
            try:
                with connection.cursor() as cursor:
                    sql="select * from PRODUCTS where category={}".format(int(categoryID))
                    cursor.execute(sql)
                    result=cursor.fetchone()
                    return {"STATUS": "SUCCESS", "CATEGORIES": result, "CODE": "200 - Success"}
            except:
                return ({"STATUS": "ERROR", "MSG": "Internal Error", "CODE": "500 - Internal error"})

# Creating a Category
@post('/category')
def create_category():
    name = request.POST.get("name")
    if name == "":
        return json.dumps({"STATUS": "ERROR", "MSG": "Name Parameter is missing", "CODE": 400})
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * from categories where name = '{}';".format(name)
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                sql2 = "INSERT into categories(name) values('{}');".format(name)
                cursor.execute(sql2)
                connection.commit()
                cat_id = cursor.lastrowid
                return json.dumps({"STATUS": "SUCCESS", "CAT_ID": cat_id, "CODE": 201,
                                   "MSG": "Category created successfully"})
            else:
                raise ValueError("category exists")
    except ValueError:
        return json.dumps({"STATUS": "ERROR", "MSG": "Category already exists", "CODE": 200})
    except Exception:
        return json.dumps({"STATUS": "ERROR", "MSG": "Internal Error", "CODE": 500})

# Delete a Category
@delete('/category/<id>')
def delete_category(id):
    try:
        with connection.cursor() as cursor:
            sql = "DELETE from categories where id = {};".format(id)
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.commit()
            return json.dumps(
                    {"STATUS": "SUCCESS", "CODE": 201, "MSG": "The category was deleted successfully"})
    except Exception as e:
        return json.dumps({"STATUS": "ERROR", "MSG": repr(e) + "Internal Error", "CODE": 500})

# Add / Edit a Product
@post('/product')
def update_product():
    id = request.POST.get("id")
    name = request.POST.get("title")
    description = request.POST.get("description")
    price = request.POST.get("price")
    image = request.POST.get("img_url")
    category = request.POST.get("category")
    favorite = 1 if request.POST.get("favorite") == "on" else 0
    try:
        with connection.cursor() as cursor:
            if id == "":
                sql = "insert into products values(0, '{}', '{}', {}, '{}', '{}', {})".format(name, description, price, image, category, favorite)
            else:
                sql = "update products set title = '{}', description = '{}', price = {}, img_url = '{}', category = {}, favorite = {} where id = {}".format(name, description, price, image, category, favorite, id)
            cursor.execute(sql)
            connection.commit()
            prod_id = cursor.lastrowid
            return json.dumps({"STATUS": "SUCCESS", "PRODUCT_ID": prod_id, "CODE": 201,
                               "MSG": "Product Created / Updated Successfully"})
    except Exception as e:
        return json.dumps({"STATUS": "ERROR", "CODE": 500, "MSG": repr(e)})

# Deleting a Product
@delete('/product/<id>')
def delete_product(id):
    try:
        with connection.cursor() as cursor:
            sql = "DELETE from products where id = {}".format(id)
            cursor.execute(sql)
            connection.commit()
            return json.dumps({"STATUS": "SUCCESS", "MSG": "Product deleted", "CODE": 201})
    except Exception as e:
        return json.dumps({"STATUS": "ERROR", "MSG": "Internal Error", "CODE": 500})


def main():
    run(host='localhost', port=7010)

if __name__ == '__main__':
    main()

