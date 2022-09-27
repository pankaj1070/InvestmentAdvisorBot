### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
from botocore.vendored import requests
import pandas as pd
import numpy as np
import json
import boto3
import csv
from io import BytesIO
import os
import io
from tabulate import tabulate


# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime= boto3.client('runtime.sagemaker')


### Load CSV file from S3 and convert it to dataframe ###
def load_csv(bucket, filename):
    
    s3 = boto3.resource('s3')
    # Open file on s3 as object
    obj = s3.Object(bucket, filename)
    # Read object as csv and convert it to dataframe
    with BytesIO(obj.get()['Body'].read()) as bio:
     df = pd.read_csv(bio, index_col=False)
    
    return (df)

### ML endpoit connector, send csv and recieve predication ###
def ml_endpoint (payload):
    
    # payload in csv format should cover input features of ML
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=payload)
    #print("MLResponse:", response)
    result = json.loads(response['Body'].read().decode())
    #print("MLresult:", result)
    pred = int(result['predictions'][0]['score'])
    predicted_label = 'A' if pred == 1 else 'B'
    
    return predicted_label
    


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]



def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },

    }
    
    return response


### Intents Handlers for EV advisor###
def ev_selection(intent_request):
    """
    Performs fulfillment for EV selection.
    """
    
    ## Get predication from endpoint in sagemaker (sample) 
    # ml_prediction= ml_endpoint("13.49,22.3,86.91,561.0,0.08752,0.07697999999999999,0.047510000000000004,0.033839999999999995,0.1809,0.057179999999999995,0.2338,1.3530000000000002,1.735,20.2,0.004455,0.013819999999999999,0.02095,0.01184,0.01641,0.001956,15.15,31.82,99.0,698.8,0.1162,0.1711,0.2282,0.1282,0.2871,0.06917000000000001")
    
    # Gets all the slots
    slots = get_slots(intent_request)

    # Gets slots' values
    acceleration = float(slots["acceleration"])
    body_style = slots["body_style"]
    car_budget = int(slots["car_budget"])
    number_seats = int(slots["number_seats"])
    power_train = slots["power_train"]
    range = int(slots["range"])
    rapid_charge = slots["rapid_charge"]
    top_speed = int(slots["top_speed"])

    # Load CSV from S3 in dataframe
    ev_df=load_csv("mj.samadi", "ElectricCarData_Clean.csv")

    # Filter dataframe with user requirements 
    ev_df=ev_df.loc[(ev_df["AccelSec"] <= acceleration) & (ev_df["PriceEuro"] <= car_budget) & (ev_df["Seats"] >= number_seats) & (ev_df["Range_Km"] >= range) & (ev_df["TopSpeed_KmH"] >= top_speed) & (ev_df["BodyStyle"] == body_style) & (ev_df["PowerTrain"] == power_train) & (ev_df["RapidCharge"] == rapid_charge)]
    ev_list=ev_df["Brand"].str.cat(ev_df["Model"], sep= " ")
    ev_list=ev_list.reset_index(drop=True)
    ev_out=ev_list.to_string(index=True)
    #ev_list_s=tabulate(ev_list, headers='keys', tablefmt='fancy_grid')
    print(ev_out)
    
    # Load Market share forcast 2022,2023 from S3 - linear regression result that prepared in SageMaker
    ev_mkt=load_csv("mj.samadi", "ev_mkt_share_forecast.csv")
    ev_mkt=ev_mkt.reset_index(drop=True)
    ev_mkt_s=tabulate(ev_mkt, headers='keys', tablefmt='fancy_grid')
    print(ev_mkt_s, "\n")

    #result_df=pd.merge(ev_df,ev_mkt, how="inner", left_on = 'Brand', right_on = 'Model')
    #print("concat:", result_df)
    

    if ev_list.empty : 
        return close(
        intent_request["sessionAttributes"],
        "Failed",
        {
            "contentType": "PlainText",
            "content": """There isn't any suitable option based on your requirements."""
        }
    )
    else:
        # Return a message with conversion's result.
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you for your information and intrest to electronic vehicle; suggested car listed in below:#\n{}\n US Market analysis of Electric Vehicle shows that following brand would have major market share in 2022 and 2023: {}\n
                """.format(ev_out , ev_mkt_s)
            }
            
        )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    #print ("intent request:", intent_request)
    # Get the name of the current intent
    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "EVPURCHASE":
        return ev_selection(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")

### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)