import random
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

app = FastAPI() # FastAPI instance. Here "app" is the reference.

# Schema is like a contract / blueprint between the frontend and backend (user and server) where the backend
# expects the frontend to send data adhering to a strict format. Similar expectations are forced on the server for the frontend.

# Posts schema. Validation done by Pydantic.

# Posts schema. Validation done by Pydantic.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None # instead of int | None in python 3.9 and older you'd have to import Optional from the typing library
                              # and use Optional[int] to do the same. Optional[X] is equivalent to X | None (or Union[X, None])

# for now we're saving posts in memory instead of a database. Will come back to it later.
my_posts = [
    {
        "title" : "title of post 1",
        "content" : "content of post 1",
        "published" : False,
        "rating" : None,
        "id" : 1,
    },
    {
        "title" : "title of post 2",
        "content" : "content of post 2",
        "published" : False,
        "rating" : None,
        "id" : 2,
    },
]


# path operation / route
@app.get("/")   # function decorator is important to make the root function an actual path operation
                # so that someone who wants to use this api can use this as an endpoint. The addition
                # of the '@' symbol is necessary to declare it as a declarator.
                # Here 'get' is the http method that the user can use. You have similar ones for post,
                # head, put, delete and other stuff.
                # the '/' is the just referencing the root path, i.e. the domain name/url of the site.

# this is a normal python function, it can have any name.
def root():
    return {"message" : "welcome to my server"} # all communications with apis is done via JSON.

"""
# note if you have multiple path operations with the same path FastAPI will execute the first one that
# matches going down the list. So get_posts won't be called if you go to <domain name>/<your path>
@app.get("/")
def get_posts():
    return {"data" : "your posts here"}
"""

# Fetch latest post
@app.get("/posts/latest")
def latest_post() -> dict:
    return {"detail" : my_posts[-1]}


# Fetch a specific post by id
@app.get("/posts/{id}")     # here the "id" field is the path parameter of the path operation. FastAPI automatically extracts this
                            # path parameter and you can just past it as a parameter to your function.
                            # NOTE PATH PARAMETERS ARE RETURNED AS STRINGS. However, if implicit conversion is possible you can 
                            # convert the path paramenter into the required datatype by specifying the target type in the function
                            # signature as a type hint/function decorator.
def get_post(id : int, response : Response) -> dict:
    post = next((post for post in my_posts if post["id"] == id), None)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND    # By declaring a parameter of type `Response` in the path operation func
        #                                                     # you can set the status code of the respone from that func.
        #                                                     # Just import the Response class and the status modules to change the 
        #                                                     # HTTP response codes. The status module contains macors/enums of all
        #                                                     # commonly used response codes.
        # return {"message" : f"post with id: {id} was not found :("}
        # a better way of doing the same is to use a python exception called HTTPException from FastAPI
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found :(")
        
    return {"post detail" : post}


# Fetches all posts from database
@app.get("/posts")
def get_posts() -> dict:
    return {"data" : my_posts}  # FastAPI automaticaly serializes the array `my_posts` into JSON format so that we can send it to 
                                # our client.


# Creates new post with specified fields in database
@app.post("/posts", status_code=status.HTTP_201_CREATED)    # as an extra feature, you can specify the response code of the path 
                                                            # operation in the path's function decorator.
def create_posts(post: Post) -> dict:
    new_post = post.model_dump(mode="json")
    id = random.randint(3, 1000000)  # generate a random id for the post.
    while (next((True for post in my_posts if post["id"] == id), False)):
        id = random.randint(3, 1000000) 
    new_post["id"] = id
    my_posts.append(new_post)

    return {"data" : new_post}


def get_index_by_id(id : int) -> int:
    idx = next((idx for idx in range(len(my_posts)) if my_posts[idx]["id"] == id), None)
    if idx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist. Could not perform operation") 
    return idx


# Delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int) -> None:
    del my_posts[get_index_by_id(id)]


# Update a post
@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def method_name(id : int, post : Post):
    idx = get_index_by_id(id)
    post_dict = post.model_dump(mode="json")
    post_dict["id"] = id
    my_posts[idx] = post_dict

    return {
        "message" : f"updated post with id: {id}",
        "data" : post_dict,
    }

# each pydantic model has a .model_dump() function that returns a dictionary of the model's fields and values. You can additionally
# set the mode parameter to "json" to make sure the output dict has only json-serializable objects as by default model_dump() can 
# output non-json-serializable python objects. 
# there is also a model_dump_json() function that's useful to dump stuff in json format instead of a dict.

"""
CRUD for anything related to posting

C - Create  (POST request)  /posts

R - Read    (GET request) ----> for getting all the posts               /posts
                           \\--> for getting a post with a specific id   /posts/:id

U - Update  (PUT/PATCH request) /posts/:id

Note: when you use PUT, you'll have to send all of the information of the specific post to update it. Even if only one field has
changed. With PATCH, you only need to send the specific field that changes so it's less costly of an operation.

D - Delete  (DELETE request)    /posts/:id

standard convention is to name the urls in plural, so if you're creating a url for posting then, it would be /posts. Similarily 
for a page for users would be /users not /user.

"""



"""
POSTGRESQL INFO

By default, Postgres uses a concept called “roles” to handle authentication and authorization. These are, in some ways, similar to
regular Unix-style accounts, but Postgres does not distinguish between users and groups and instead prefers the more flexible term
“role”.

Upon installation, Postgres is set up to use peer authentication, meaning that it associates Postgres roles with a matching 
Unix/Linux system account. If a role exists within Postgres, a Unix/Linux username with the same name is able to sign in as that 
role.

The installation procedure created a user account called postgres that is associated with the default Postgres role. In order to
use Postgres, you can log into that account.

There are a few ways to utilize this account to access Postgres.
Switching Over to the postgres Account

Switch over to the postgres account on your server by typing:

`sudo -i -u postgres`

Then start the PostgreSQL Prompt

`psql`

You "should" see something like this:

`postgres=#  `

You can also do all this and send commands directly to the Postgresql prompt by doing

`sudo -u <username assoicated with postgres> <postgresql command>`

so that will translate to (in order to start): `sudo -u postgres psql` because upon installation the current default username is 
postgres. Otherwise you can create a new username for running postgres using the following command:

`sudo -u <current_username> createuser --interactive` e.g. sudo -u postgres createuser --interactive

and accordingly create a new database with the same name as that's how postgres does authentication.

`sudo -u <current_username> createdb <new_username>` e.g. sudo -u postgres createdb adarshdb


## TABLES

Any subject or event in an application is represented by a table in the database. These tables can then be related to each other in
some way, shape or form, hence the term relational database. For example, lets say we have three tables: user, products, purchases
The user table can be related to the purchases table and then that can be related to the products table depending on the what the 
user purchased. 

## Columns VS Rows

Each table has rows and columns, cols represent different attributes of an entry in the table. Each row then represents a single
entry. For example in the users table we can have cols for ID, Name, Age and Sex. Each row would then indicate the entry for a
single user.

## Postgres Datatypes

Postgres has datatypes just like normal programming languages like, numeric(int, decimal, precision), text(varchar, text),
bool(boolean), sequence(array). The python equivs are int, float, string, bool and list respectively.

## Primary Key

Each table needs a column or a group of columns that uniquely identifies each row in a table called a primary key. A table can 
only have one and only one primary key and each key must be unique.

It's upto choice which column you prefer to serve as the primary key.

## Constraints

1. UNIQUE - a 'UNIQUE' constraint can be applied to any column to make sure every record has a unique value for that column
2. NULL - By default when adding a new entry to a database a column can be left blank. When a column is left blank it has a 
          NULL value. If you need a column to be properly filled in to create a new record a NOT NULL constraint can be added to 
          the column to ensure that the column is never left blank.

          
ALTER ROLE <role_name> WITH <option> - a really powerful tool

🔑 Permission and Attribute Options You Can Set or Reset

| Option                          | Description                                                                |
| ------------------------------- | -------------------------------------------------------------------------- |
| `SUPERUSER` / `NOSUPERUSER`     | Grant or revoke superuser status                                           |
| `CREATEDB` / `NOCREATEDB`       | Allow or disallow creating databases                                       |
| `CREATEROLE` / `NOCREATEROLE`   | Allow or disallow creating (and altering) roles                            |
| `INHERIT` / `NOINHERIT`         | Allow or disallow inheriting permissions of roles this role is a member of |
| `LOGIN` / `NOLOGIN`             | Allow or disallow login ability (i.e., can this role authenticate)         |
| `REPLICATION` / `NOREPLICATION` | Allow or disallow streaming replication connections                        |
| `BYPASSRLS` / `NOBYPASSRLS`     | Allow or disallow bypassing Row-Level Security policies                    |

🛠 Other common role attribute modifications:

| Command                   | Description                                 |
| ------------------------- | ------------------------------------------- |
| `PASSWORD 'password'`     | Set or change role’s password               |
| `VALID UNTIL 'timestamp'` | Set expiration time for the role’s password |
| `CONNECTION LIMIT n`      | Set max concurrent connections (n ≥ 0)      |
| `IN ROLE role1, role2`    | Add role to memberships of other roles      |
| `ROLE role1, role2`       | Same as above (alternate syntax)            |
| `ADMIN ROLE role1, role2` | Make this role admin of other roles         |
| `USER`                    | Deprecated alias for LOGIN                  |


"""
