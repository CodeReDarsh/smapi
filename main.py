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
