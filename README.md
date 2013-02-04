![web component logo](http://i50.tinypic.com/2ezms1l.png)


##Introduction

Utilizing a scissor, paper and a little glue, jitte was kickstarted in a weekend. It's primary purpose is web service testing, but practically it can even drive simple webpages.
Despite the fact that it's written in Python, it's actually used through the command line, where it requires only two positional arguments, the first one is the path to the test script (see below), and the second argument is a path where the results of the tests will be saved. Plain and simple, like:

    $ ./jitte.sh samples/get-get/test.json ~/testrun1
    Requesting => https://api.twitter.com/1/users/show.json
    Requesting => http://maps.googleapis.com/maps/api/geocode/json
    Requesting => https://api.twitter.com/1/users/show.json
    ===================
    Tests run: 3
    0 failed. 3 passed.
    ===================

http://i47.tinypic.com/1glp9c.png

##Installation

    sudo python setup.py install

Somewhere, near the end of the installation you will see something like:

    Installed /usr/local/lib/python2.7/dist-packages/jitte-0.1-py2.7.egg

now you can start jitte with ./jitte.sh from here:

    /usr/local/lib/python2.7/dist-packages/jitte-0.1-py2.7.egg/jitte

##Test Scripts

One could easily pick up the meta language for writing test scripts, as it uses the well known JSON format, with a couple of chosen keywords. By peeking into the samples folder it should be pretty straightforward what is going on, but nevertheless it deserves a little explanation. Let's look at a sample step:

    "1" : {
            "url" : "http://www.google.com/", 
            "method" : "GET",
            "send_data" : [
                {
                    "param_name" : {
                        "value" : "something",
                        "type" : "static"
                    },
                    "param_value" : {
                        "value" : "345",
                        "type" : "static"
                    }
                }
            ],
            "headers" : {
                "accept": "text/html",
                "accept-encoding": "none"
            },
            "assume" : [
                {
                    "type" : "status_code",
                    "expected": "200",
                    "pass_if" : "eq"
                }
            ],
            "next" : "2"
        },

A test is separated into one or more steps, and we are looking at the first step of an imaginary test case. The key "1" at the beginning indicates the id of the current step. The value assigned to it is an object containing the following keys:
* 'url' - the URL of the target service / page
* 'method' - the request method that should be used for the current step
* 'send_data' - a list of objects, where each object specifies the parameter name and value that will be posted or added to the url as query string. These parameters can be specified in several ways, it may be 'static' which means it's hardcoded into the test configuration file or it can be a value got from the previous step result. In those cases, the value can be retrieved either by an XPath expression (if the previous response was XML or HTML), or it can be retrieved from a JSON response using a list of strings, in which case the program would traverse the JSON response tree, and find the value under the last key specified in the list.
* 'headers' - an object containing key/value pairs, representing the request header names and values
* 'assume' - a list of objects where each object is an assumption about the expected value, snippet or status code of the response. The assumption type specifies what will be verified in the response, the status code, the whole response as string or to find an exact value in the response, either by using an XPath expression (for XML / HTML files) or by using a list of strings (for JSON responses). The two latter checks would require one additional parameter, a value to be compared with the found one. The 'pass_if' parameter is just a logical operator, so the assumption will evaluate to true if the response is equal, not equal, contains or does not contain the expected value.
* 'next' - indicates the next step where the program will jump after completing the current step.
