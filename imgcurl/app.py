from flask import Flask, redirect, abort, make_response, request
from models import ImageLink, RedisManager, ObjectNotFoundError
import settings

app = Flask(__name__)
app.config.from_object('settings')

ImageManager = RedisManager(ImageLink)

@app.route('/<key>', methods=['GET'])
def get_image(key):
    try:
        #temporal hasta que componga el "ORM"
        img = ImageManager.get(key)
        return redirect(img.value)
    except ObjectNotFoundError, e:
        app.logger.critical("%s: %s", type(e), e.message)
        abort(404)
    except Exception, e:
        app.logger.critical("%s: %s", type(e), e.message)
        abort(500)

@app.route('/image/add/', methods=['POST'])
def add_image():
    post_data = request.form
    if not 'api_key' in post_data:
        abort(500)
    if not 'key' in post_data:
        abort(500)
    if not 'value' in post_data:
        abort(500)

    if settings.API_KEY == post_data['api_key']:
        try:
            img = ImageLink(key=post_data['key'], value=post_data['value'])
            img.save()
            return make_response("OK", 200)
        except Exception, e:
            app.logger.critical("%s: %s", type(e), e.message)
            abort(500)
    else:
        abort(500)

@app.route('/image/delete/', methods=['POST'])
def delete_image():
    post_data = request.form
    print post_data
    if not 'api_key' in post_data:
        app.logger.critical("no_api")
        abort(500)
    if not 'key' in post_data:
        app.logger.critical("no key")
        abort(500)

    if settings.API_KEY == post_data['api_key']:
        try:
            img = ImageManager.get(post_data['key'])
            img.delete()
            return make_response("OK", 200)
        except Exception, e:
            app.logger.critical("%s: %s", type(e), e.message)
            abort(500)
    else:
        app.logger.critical("wrong API")
        abort(500)

    pass

@app.errorhandler(404)
def not_found(error):
    response = make_response('Not Found', 404)
    return response

@app.errorhandler(500)
def internal_error(error):
    response = make_response('Internal Server Error', 500)
    return response

if __name__ == "__main__":
    app.run()
