# ECE1779A3
ECE1779A3

Setup:
pip install flask
pip install Pillow
pip install zappa
pip install Flask-AWSCognito
pip etc.

To setup for the zappa (https://github.com/dbjohnson/zappa-quick-start):
1. Setup a Cognito user pool according to step 4 of the link above. In my case I enabled the Username option, and added email as required in 'Attributes'. And also enabled 'Authorization code grant' in App Client Settings.
2. Modify the zappa_settings.json directly, OR rename it as a backup and then use "zappa init" and then match with your configurations (S3, Cognito, app.webapp, etc.)
3. Modify app/__init__.py so that the cognito configurations match with you Cognito user pool
4. Attach some more policies to the IAM Role: AmazonAPIGatewayAdministrator, AmazonEventBridgeFullAccess, AWSCloudFormationFullAccess, and AWSLambda_FullAccess
5. Use "zappa deploy dev"
6. Replace the callback urls both in app/__init__.py and also in Cognito 'App Client settings' with the the deployed link
7. Do "zappa update", and it should be good to go

To setup for DynamoDb:
1. Create a table called 'users' with only 'username' as key
2. Attach AmazonDynamoDbFullAccess policy to the IAM Role

Other notes:
Conda: if u r using conda, activate VE w/ conda does not work with zappa, use venv instead 
deploy name: pls use 'dev' such that the root url appears to be {.../dev}, some of api calls are hard coded strings. Double check when using getRootUrl to see if it is correct 

To setup for backgroud lambda:
1. Create a lambda function from blueprint "microservice-http-endpoint"
2. Copy the code from app/static/scripts/index.js (renamed to backgroundlambda.js) into the code section
3. Modify the bucket name in the code with the name of your own bucket
4. Deploy the code, maybe test it by plainly opening it and then go to the static hosting website in s3 namely "dashboard.html"
5. Modify the "Go To Dashboard" link in app/teamplates/index.html, so that is points to the static hosting website in your s3 bucket
6. Setup cron job

To setup cron job:
1. Modify and copy app/static/scripts/cronjob.sh to a place like Desktop
2. Run "crontab -e" from terminal
3. Add the following line to the very end of the crontab file, and then save the file for a 5 minute recurring cron job
*/5 * * * * bash ~/Desktop/cronjob.sh
4. It should say something like "crontab: installing new crontab", which means it is good
5. Do some testing to make sure it actually is doing the cron job, observe a message every 5 minutes from CloudWatch lambda logs
6. To stop it, run crontab and comment out the line you just added with #
