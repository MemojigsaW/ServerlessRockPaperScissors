const AWS = require('aws-sdk');

const dynamo = new AWS.DynamoDB.DocumentClient();
const s3 = new AWS.S3({ apiVersion: '2006-03-01' });

/**
 * Demonstrates a simple HTTP endpoint using API Gateway. You have full
 * access to the request and response payload, including headers and
 * status code.
 *
 * To scan a DynamoDB table, make a GET request with the TableName as a
 * query string parameter. To put, update, or delete an item, make a POST,
 * PUT, or DELETE request respectively, passing in the payload to the
 * DynamoDB API as a JSON body.
 */
exports.handler = async (event, context) => {
    //console.log('Received event:', JSON.stringify(event, null, 2));

    let body;
    let statusCode = '200';
    const headers = {
        'Content-Type': 'application/json',
    };

    try {
        body = await dynamo.scan({ TableName: 'users' }).promise();
        var list = [];
        var computerWins = 0;
        var computerGames = 0;
        for (var key in body['Items']){
            var val = body['Items'][key];
            var numWins = val['numWins'];
            var numLoses = val['numLoses'];
            var numTies = val['numTies'];
            var numGames = numWins+numLoses+numTies;
            list.push({'user': val['username'], 'numWins': numWins, 'winRate': numWins/numGames});
            computerGames+=numGames;
            computerWins+=numLoses;
        }
        list.push({'user': 'Anonymous G.O.D. of RockPaperScissors', 'numWins': computerWins, 'winRate': computerWins/computerGames});
        list.sort(function(a, b){return b['winRate']-a['winRate']});

        var html = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><meta charset="utf-8"><title> Global Dashboard</title></head> <body><h1> Global Dashboard </h1>'
        html+= '<table><thead> <th>Rank</th> <th>User</th> <th>Number of Wins</th> <th>Total Win Rate</th> </thead>'

        for (var i = 0; i < list.length; i++)
        {
            var rank = i+1
            html+= '<tr> <td>'+ rank +'</td> <td>'+ list[i]['user'] +'</td> <td>'+ list[i]['numWins'] +'</td> <td>'+ list[i]['winRate']*100 +'% </td>'
        }
        html += '</table> <button onclick="goBack()">Go Back</button><script>function goBack() {window.history.back();}</script> </body></html>'

        // putObject to S3
        console.log(html)
        var params = {
            Bucket : 'ece1779a3alex',
            Key : 'dashboard.html',
            Body : html,
            ACL: 'public-read',
            ContentType: 'text/html'
        }
        const response = await s3.upload(params).promise();
        console.log('Response: ', response);

    } catch (err) {
        statusCode = '400';
        body = err.message;
        console.log(err, err.message, err.stack)
    } finally {
        body = JSON.stringify(body);
    }
    return {
        statusCode,
        body,
        headers,
    };
};