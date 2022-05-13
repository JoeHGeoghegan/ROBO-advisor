### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


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

### Functionality Helper Functions ###
def parse_float(n):
    """
    Attempts to Parse passed variable to float.
    """
    try:
        return float(n)
    except ValueError:
        return float("nan")

## Data Validation ###
def validate_data(age,investment_amount,intent_request):
    """
    Validates the data provided by the user.
    """
    # Validate that the user is over 21 years old
    if age is not None:
        age = parse_float(age)
        if age < 21:
            return build_validation_result(
                False,
                "age",
                "You should be at least 21 years old to use this service, "
                "please be older.",
            )

    # Validate the investment amount, it should be > 0
    if investment_amount is not None:
        investment_amount = parse_float(
            investment_amount
        )  # Since parameters are strings it's important to cast values
        if investment_amount <= 0:
            return build_validation_result(
                False,
                "usdAmount",
                "The amount to convert should be greater than zero, "
                "please provide a correct amount in USD to invest.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    slots = get_slots(intent_request)
    first_name = slots["firstName"]
    age = slots["age"]
    investment_amount = slots["investmentAmount"]
    risk_level = slots["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        validation_result = validate_data(age,investment_amount,intent_request)

        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    weight_risk_lookup = {'None': [1,0],
                'Very Low': [.8,.2],
                'Low': [.6,.4],
                'Medium': [.4,.6],
                'High': [.2,.8],
                'Very High': [0,1]
    }
    weight = weight_risk_lookup[risk_level]
    initial_recommendation = (f'{weight[0]*100}% bonds (AGG), {weight[1]*100}% equities (SPY). ' +
                                f'This is ${weight[0]*parse_float(investment_amount):.2f} of bonds and ' +
                                f'${weight[1]*parse_float(investment_amount):.2f} of equities')
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
