from flask import Flask
import config as cfg
#from flask_cors import CORS
from flask_awscognito import AWSCognitoAuthentication

webapp = Flask(__name__)
webapp.secret_key = cfg.SECRET_KEY
#CORS(webapp)
# webapp.config['AWS_DEFAULT_REGION'] = 'us-east-1'
# webapp.config['AWS_COGNITO_DOMAIN'] = 'ece1779a3.auth.us-east-1.amazoncognito.com'
# webapp.config['AWS_COGNITO_USER_POOL_ID'] = 'us-east-1_wv9y253RA'
# webapp.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '614teujra7t8j4mjmk5cfathqe'
# webapp.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = 'f9leavn801fv1he204fkpcofd3keggoai8cvt07fjic63o1v6p3'
# webapp.config['AWS_COGNITO_REDIRECT_URL'] = 'https://1sgvbvrbka.execute-api.us-east-1.amazonaws.com/dev/aws_cognito_redirect'
webapp.config['AWS_DEFAULT_REGION'] = 'us-east-1'
webapp.config['AWS_COGNITO_DOMAIN'] = 'ece1779a3alan.auth.us-east-1.amazoncognito.com'
webapp.config['AWS_COGNITO_USER_POOL_ID'] = 'us-east-1_J5dJ0zKRa'

webapp.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '1ap58tjv0odikahc954993jl41'
webapp.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = '1hjl069echqcgkhgibliiei4h99qhqke2g5g5ao12cj15aamvb9e'

webapp.config['AWS_COGNITO_REDIRECT_URL'] = 'https://v7xn98u1ue.execute-api.us-east-1.amazonaws.com/dev/aws_cognito_redirect'

webapp.aws_auth = AWSCognitoAuthentication(webapp)

from app import IndexPage
from app import VideoPage
from app import AWSRekog
