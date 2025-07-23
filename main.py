from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI() # FastAPI instance. Here "app" is the reference.


# Schema is like a contract / blueprint between the frontend and backend (user and server) where the backend
# expects the frontend to send data adhering to a strict format. Similar expectations are forced on the server for the frontend.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None 

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

# this get_posts finally executes.
@app.get("/posts")
def get_posts():
    return {"data" : "your posts are here! finally.."}

@app.post("/posts")
def create_posts(post: Post): # type: ignore
    print(post.title)
    print(post.content)
    print(post.published)
    print(post.rating)
    return post.dict()

# each pydantic model has a .dict() function that returns a dictionary of the model's fields and values.

"""
CRUD for anything related to posting

C - Create  (POST request)  /posts

R - Read    (GET request) ----> for getting all the posts               /posts
                           \--> for getting a post with a specific id   /posts/:id

U - Update  (PUT/PATCH request) /posts/:id

Note: when you use PUT, you'll have to send all of the information of the specific post to update it. Even if only one field has
changed. With PATCH, you only need to send the specific field that changes so it's less costly of an operation.

D - Delete  (DELETE request)    /posts/:id

standard convention is to name the urls in plural, so if you're creating a url for posting then, it would be /posts. Similarily 
for a page for users would be /users not /user.



"""
