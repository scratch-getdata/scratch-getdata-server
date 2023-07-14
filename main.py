import os
import time
try:
    from flask import render_template, send_file, request
    from flask import Flask, jsonify
    from flask import abort
    from flask import url_for
    from flask_autoindex import AutoIndex
    import json
    import io
    import re
    import requests
    from bs4 import BeautifulSoup
    from PIL import Image
    from requests.exceptions import RequestException
    from colorama import Fore, Back, Style
except:
    print(Fore.RED + "Error: ModuleNotFound trying to install via requirements.txt" + Fore.RESET)
    try:
        os.system('pip install -r requirements.txt')
    except:
        print(Fore.RED + "Error: Cannot install via requirements.txt the process may exit." + Fore.RESET)
        exit(1)
    time.sleep(1)
    from flask import render_template, send_file, request
    from flask import Flask, jsonify
    from flask import abort
    from flask import url_for
    from flask_autoindex import AutoIndex
    import json
    import io
    import re
    import time
    import requests
    from bs4 import BeautifulSoup
    from PIL import Image
    from requests.exceptions import RequestException
    from colorama import Fore, Back, Style
    print(Fore.GREEN + "Install and import completed without any errors." + Fore.RESET)

app = Flask('app')

time.sleep(1)

print(Fore.GREEN + "Flask Initialized." + Fore.RESET)

# Require Define Functions:

def get_scratch_data(url):
    response = requests.get(url)
    response.raise_for_status()

    try:
        return json.loads(response.text)
    except ValueError:
        try:
            return int(response.text)
        except ValueError:
            return response.text

def get_scratch_data_nojson(url):
    response = requests.get(url)
    response.raise_for_status()

    return response

print(Fore.GREEN + "Important functions defined." + Fore.RESET)


# Flask routes and non important definitions


@app.route('/')
def home():
   return render_template('index.html')
if app == '__main__':
   app.run()

@app.route('/updates/')
def update():
    with open('static/updates.txt', 'r') as f:
        updates_content = f.readlines()
    return render_template('updates.html', updates=updates_content)

@app.route('/updates/test/')
def updatet():
   return render_template('update-test.html')

@app.route('/python/docs/')
def updatet():
   return render_template('python-docs.html')

@app.route('/install/')
def install():
   return render_template('install.html')

@app.route('/why/')
def why():
   return render_template('why.html')

@app.route('/docs')
def udocs():
   return render_template('docs.html')


# Code is not shown becuase it contains web scraping


@app.route("/get/aboutme/<username>/")
def about_me(username):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/users/{username}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.text:
            try:
                data = json.loads(response.text)
                if "code" in data and data["code"] == "NotFound":
                    abort(404)
                    return "User does not exist"
                elif "username" in data and "profile" in data:
                    about_me = data["profile"].get("bio", "")
                    return about_me
                else:
                    return "Invalid response structure"
            except json.decoder.JSONDecodeError:
                return "Invalid response structure"
        else:
            return "No data received"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"



@app.route("/get/messages/<username>/")
def get_messages(username):
    try:
        response = requests.get(f"https://explodingstar.pythonanywhere.com/scratch/user/messages/{username}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.text:
            try:
                data = json.loads(response.text)
                count = data["count"]
                return str(count)
            except (json.decoder.JSONDecodeError, KeyError):
                abort(404)
                return "Invalid response structure"
        else:
            return "No data received"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/project/creator/<project_id>/")
def project_creator(project_id):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "author" in data and "username" in data["author"]:
                creator = data["author"]["username"]
                return creator
            else:
                return "Project creator not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/name/<project_id>/")
def project_name(project_id):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "title" in data:
                name = data["title"]
                return name
            else:
                return "Project name not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/notes_and_credits/<project_id>/")
def project_notes_and_credits(project_id):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "description" in data:
                description = data["description"]
                return description.strip()  # Return the description as-is
            else:
                return "Project description not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/instructions/<project_id>/")
def project_instructions(project_id):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "instructions" in data:
                instructions = data["instructions"]
                return instructions.strip()  # Return the instructions as-is
            else:
                return "Project instructions not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/blocks/<project_id>/")
def project_blocks(project_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/project/info/{project_id}"
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "ProjectNotFoundError":
                    abort(404)
                    return "Project not found"
                elif error_message == "UserNotValidError":
                    abort(404)
                    return "Invalid user"
                else:
                    return "Error: " + error_message
            elif "metadata" in data and "blocks" in data["metadata"]:
                blocks = data["metadata"]["blocks"]
                return str(blocks)
            else:
                return "Number of blocks not found"
        elif response.status_code == 404:
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/forum/title/<post_id>/")
def forum_title(post_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/forum/topic/info/{post_id}"
        )
        print(response.status_code)
        print(response.content)
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "PostNotFoundError":
                    abort(404)
                    return "Post not found"
                elif error_message == "PostNotValidError":
                    abort(404)
                    return "Invalid post ID"
            elif "title" in data and data["title"] is not None:
                title = data["title"]
                return title
                abort(404)
        return "Username not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/forum/category/<post_id>/")
def forum_category(post_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/forum/topic/info/{post_id}"
        )
        print(response.status_code)
        print(response.content)
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "TopicNotFoundError":
                    abort(404)
                    return "Post not found"
                elif error_message == "TopicNotValidError":
                    abort(404)
                    return "Invalid post ID"
            elif "category" in data and data["category"] is not None:
                category = data["category"]
                return category
        return "Username not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/user/country/<username>/")
def scratch_user_country(username):
    try:
        response = requests.get(
            f"https://explodingstar.pythonanywhere.com/scratch/user/profile/{username}"
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if "country" in data["profile"]:
                country = data["profile"]["country"]
                return country
            else:
                return "Country information not available"
        elif response.status_code == 404:
            abort(404)
            return "User does not exist"
        else:
            return "Failed to retrieve user profile"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/ocular/user/status/<username>/")
def user_status(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        status = data["status"]
        return status
    else:
        abort(404)
        return jsonify({"error": "User not found"})

@app.route("/get/ocular/user/color/<username>/")
def user_color(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data and data["error"] == "no user found":
            abort(404)
            return jsonify({"error": "User not found"}), 404
        else:
            status = data["color"]
            return status
    else:
        abort(response.status_code)

@app.route("/get/ocular/user/updated_time/<username>/")
def user_updater(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data and data["error"] == "no user found":
            abort(404)
            return jsonify({"meta": {"error": "User not found"}, "data": None}), 404
        else:
            updated = data["meta"]["updated"]
            return jsonify(updated)
    else:
        abort(response.status_code)


@app.route("/get/user/profilepic/<size>/<username>/")
def profile_pic(size, username):
    try:
        image_url = f"https://scratchimagedatabase.kokoiscool.repl.co/user/{size}/{username}.png"
        response = requests.get(image_url)
        
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            return send_file(image_data, mimetype='image/png')
        elif response.status_code == 404:
            abort(404)
            return "User does not exist"
        else:
            return "Failed to retrieve user profile"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/studio/title/<studioid>/")
def studio_title(studioid):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/studios/{studioid}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if "title" in data:
                title = data["title"]
                return title
            else:
                return "Studio title not found"
        elif response.status_code == 404:
            abort(404)
            return "Studio not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/studio/description/<studioid>/")
def studio_description(studioid):
    try:
        response = requests.get(f"https://api.scratch.mit.edu/studios/{studioid}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if "description" in data:
                description = data["description"]
                return description
            else:
                return "Studio description not found"
        elif response.status_code == 404:
            return "Studio not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route('/get/studio/count_curators/<studioid>')
def count_curators(studioid):
    url = f"https://api.scratch.mit.edu/studios/{studioid}/curators"
    data = get_scratch_data(url)

    if isinstance(data, list):
        count = sum(1 for curator in data if 'username' in curator.keys())
    else:
        count = 0

    return str(count)

@app.route('/get/studio/count_managers/<studioid>')
def count_managers(studioid):
    url = f"https://api.scratch.mit.edu/studios/{studioid}/managers"
    data = get_scratch_data(url)

    try:

        if isinstance(data, list):
            count = sum(1 for manager in data if 'username' in manager.keys())
        else:
            count = 0

        return str(count)
    except:
        abort(404)

@app.route('/get/user/non-processed/<username>/')
def get_non_proccessed_username(username):
    try:
      url = f"https://api.scratch.mit.edu/users/{username}"
      data = get_scratch_data(url)
      return jsonify(data)
    except:
      abort(404)

@app.route('/get/project/non-processed/<projectid>/')
def get_non_proccessed_project(projectid):
    try:
      url = f"https://api.scratch.mit.edu/projects/{projectid}"
      data = get_scratch_data(url)
      return jsonify(data)
    except:
      abort(404)
  
@app.route('/get/user/user-exist/<user>/')
def checkuseralive(user):
    url = 'https://api.scratch.mit.edu/accounts/checkusername/' + user
    data = get_scratch_data(url)
    print(data)

    if data['msg'] != 'username exists':
        return "false"
    else:
        return "true"

@app.route('/get/user/last_follower/<username>/')
def last_follower(username):
    url = f"https://api.scratch.mit.edu/users/{username}/followers/?limit=1&offset=0"
    response = get_scratch_data(url)

    try:
        if isinstance(response, list) and len(response) > 0:
            last_follower = response[0]['username']
        else:
            last_follower = "No followers"
    except (KeyError, TypeError):
        last_follower = "Error retrieving last follower"

    return last_follower




#Internel commands (Is not public)

@app.route("/internal/restart")
def restart():
    provided_secret = request.args.get("string")

    # If the string parameter does not exist, use the Authorization header
    if not provided_secret:
        provided_secret = request.headers.get('Authorization')

    if provided_secret == os.environ['internal_secret'] and request.path == "/internal/restart":
        # Return the "Restarting..." message
        os.kill(os.getpid(), 9)
        return "Restarting..."
    else:
        abort(401)

@app.route("/internal/")
def internel_error():
  abort(401)

#Testing use
#Code removed

#Other things and error handlers

@app.route("/keep-alive/")
def keep_alive():
    return '{"Status": "Up"}'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400

@app.errorhandler(405)
def page_not_found(e):
    return render_template('405.html'), 400


app.run(host='0.0.0.0', port=8080)

print(Fore.GREEN + "Flask Ready." + Fore.RESET)

print(Fore.GREEN + "Flask Webserver started" + Fore.RESET)
