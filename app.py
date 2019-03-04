import json
from flask import Flask, jsonify, render_template, request
from flask_jwt_extended import JWTManager, create_access_token, \
    create_refresh_token, get_jwt_identity, jwt_refresh_token_required, \
    jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies


# TODO : remove when run on production
from flask_ngrok import run_with_ngrok
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

app = Flask(__name__)

# POSTGRES = {
#     'user': 'postgres',
#     'pw': 'admin',
#     'db': 'peavoltadb',
#     'host': 'localhost',
#     'port': '5432',
# }
# app.config['DEBUG'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Config for non expiration token
app.config['JWT_TOKEN_LOCATION'] = ['json']
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)

# TODO : Uncomment for ngrok
# run_with_ngrok(app)

# * Important this is static  method.
def init_db():
    # ? Should Mapping Engine by models.py intead
    dbengine = create_engine('postgresql+psycopg2://postgres:admin@localhost/peavoltadb' ) 
    # create a configured "Session" class
    Session = sessionmaker(bind=dbengine)
    # create a Session
    session = Session()
    return session
# * -------------------------------------------------------------------------------

@app.route("/", methods=['GET'])
def status():    
    return jsonify({'msg' : 'API ONLINE'}), 200

@app.route('/token/register', methods=['POST'])
def register():
    try:
        print('Register User')
        data = json.loads(request.data)
        customer = models.Customer(data)
        sess = init_db()
        sess.add(customer)
        sess.commit()
        return jsonify({'msg': "Register Successful"}), 200

    except Exception as err:
        print(err)
        return jsonify({'login': False, 'msg': 'Register fail'}), 401

@app.route('/token/login', methods=['POST'])
# # TODO : Remove print function for production
def login():
    print("Login")
    print(request)
    data = json.loads(request.data)
    user = data.get('login', None)
    password = data.get('passwd', None)
    try :
        sess = init_db()
        query = sess.query(models.Customer).filter(models.Customer.login == user, models.Customer.passwd == password)
        result = query.first()

        if result:

            ret = {
                'msg':'Login Succesful',
                'access_token':create_access_token(identity=user),
                'refresh_token':create_refresh_token(identity=user)
            }

            sess.close()
            return jsonify(ret), 200

        else :
            sess.close()
            return jsonify({"msg": "Problem in Authentication"}), 401

    except Exception as err:
        print(err)
        sess.close()
        return jsonify({'Error :', err}), 401

@app.route('/token/refresh', methods=['GET', 'POST'])
@jwt_refresh_token_required
def refresh_token():
    print('Refresh Token')
    try :
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return ({'msg': 'Session Alive', 'status': True, 'access_token': access_token}), 200

    except Exception as Err:
        print(Err)
        return jsonify({'msg':'Session Expired', 'status': False}), 401


@app.route('/api/getuserinfo', methods=['POST'])
@jwt_required
def get_user_info():
    sess = init_db()
    username = get_jwt_identity()
    print(username)
    try:
        
        # user = Customer.query.filter(Customer.login == username).first()
        query = sess.query(models.Customer).filter(models.Customer.login == username)
        user = query.first()
        res = {'id': user.id,
               'name': user.name,
               'mobile': user.mobile,
               'email': user.email,
               'avatar': user.avatar,
        }
        print("----------------------------")
        return jsonify(res), 200

    except Exception as err :
        print(err)
        return jsonify({'msg': 'Error : {}'.format(err), 'status': False}), 401



@app.route('/api/remotetx', methods=['POST'])
@jwt_required
def remote_tx():
    userlogin = get_jwt_identity()
    data = json.loads(request.data)
    cp_id = data.get('chargepoint', 'None')
    command = data.get('command', 'None')
    if command == 'START' and cp_id != 'None':
        print("Remote Start Transaction")
        # Do stuff MQTT here
        # TODO : Send command MQTT to Gateway
        return jsonify({"msg": "Start Transaction Success"}), 200

    elif command == 'STOP' and cp_id != 'None':
        print("Remote  Stop Transaction")
        # Do stuff MQTT here
        # TODO : Send command MQTT to Gateway
        return jsonify({"msg": "Stop Transaction Success"}), 200

    else :
        return jsonify({"msg": "Error in Command"}), 404


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',port='5000')
