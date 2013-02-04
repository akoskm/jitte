# Intro

The following example will give you a basic introduction to jitte's testing methodology, workflow and flexibility.
Note that the test scenarios are for demonstration purpose.

# Scenario

1. retrieve TwitterAPI's profile, check if the "location" element of the response equals to "San Francisco, CA"
2. pass the value of the "location" field obtained in the previous response to a Google Map web service, check if the response code got from Google Map service equals to 200
3. repeat the first step but now instead of comparing the value of "location", check only that it's not empty

# Line-by-line walkthrough:

Every test structure begins with the order of the test case. Since you can execute tests consecutively it is important to order them.

    "1" : { }

The syntax pretty-much tells everything about the following lines:

    "url" : "https://api.twitter.com/1/users/show.json", 
    "method" : "GET"

the "url" and the "method" are the URL of the service you are interacting with and HTTP method you are using during this interaction.

In the "send_data" block you can define the parameters you are sending to the service defined with "url". The send_data block has the following structure:

    "send_data" : [
        {
            "param_name" : {
                "value" : "screen_name",
                "type" : "static"
            },
            "param_value" : {
                "value" : "TwitterAPI",
                "type" : "static"
            }
        }+
    ]

In the param_name block you specify the name of the parameter. This name can be static (ie. string) or it can be obtained from the previous response, as the value of a property in a json structure. For the sake of simplicity in this example, the name is static, and since we are going to fire a GET request, it will appear as the query parameter of the "url", like:

    https://api.twitter.com/1/users/show.json?screen_name

The purpose of the param_value block is to supply a value for the previously defined param_name. Just like the name, it can be obtained either from the previous xml or json response, or as a static string. Again for simplicity we are going to use a static value, TwitterAPI. Finally, the "url" so far has the following form:

    https://api.twitter.com/1/users/show.json?screen_name=TwitterAPI

The same rules apply for the next param_name, param_value pair.

The following block, called "assume" is where we actually execute our tests, check our assumptions.
In this test the assume block has the following structure:

    "assume" : [
        {
            "type" : "status_code",
            "pass_if" : "eq",
            "value": "200"
        },
        {
            "type" : "json",
            "assumed" : ["location"],
            "pass_if" : "eq",
            "value": "San Francisco, CA"
        }
    ]

which briefly means: the first assumption is that the status_code of the response will be equal to 200.

The second assumption is a bit more powerful. With the type attribute you tell jitte to specify "how" it should look for the assumed value. In this case it is json, meaning that jitte will look for the "location" element in the received json response and the assumtion will pass if the found value equals to "San Francisco, CA".

Now take a look at our second test case. This shows you a new way to obtain param_value. In your previous test it was a static string, but here:

    "param_name" : {
        "value" : "address",
        "type" : "static"
    },
    "param_value" : {
        "value" : ["location"],
        "type" : "json"
    }

you instruct jitte to look at the "location" element of the previous json response and attach that value to the request url. Since the "location" element of the previous response - according to our test - was "San Francisco, CA", your url so far should look like:

    http://maps.googleapis.com/maps/api/geocode/json?address=San%20Francisco%2C%20CA
