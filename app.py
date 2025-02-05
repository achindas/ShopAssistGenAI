from flask import Flask, redirect, url_for, render_template, request
from functions import (
    initialize_conversation,
    get_chat_completions,
    moderation_check,
    compare_laptops_with_user,
    recommendation_validation,
    product_map_layer
)
import openai
import pandas as pd
import json
import os

# Read the OpenAI API key
openai.api_key = open("OPENAI_API_Key.txt", "r").read().strip()
os.environ['OPENAI_API_KEY'] = openai.api_key

app = Flask(__name__)

chat_gui = []
# Let's initialise the conversation
conversation = initialize_conversation()
introduction = get_chat_completions(conversation).content
chat_gui.append({'bot':introduction})
top_3_laptops = None

# Check if updated_laptop.csv file is available in current directory. If available, no action is required
# If not available, create it by calling product_map_layer function
filename = "updated_laptop.csv"
if not os.path.exists(filename):
    laptop_df= pd.read_csv('laptop_data.csv')
    ## Create a new column "laptop_feature" that contains the dictionary of the product features
    laptop_df['laptop_feature'] = laptop_df['Description'].apply(lambda x: product_map_layer(x))

    # Save the file for future reference
    laptop_df.to_csv("updated_laptop.csv",index=False,header = True)

# Create the API for default url
@app.route("/")
def default_func():
    global chat_gui, conversation, top_3_laptops
    return render_template("chat_gui.html", chat_thread = chat_gui)

# Create the API to end the conversation
@app.route("/exit", methods = ['POST','GET'])
def exit_conv():
    global chat_gui, conversation, top_3_laptops
    chat_gui = []
    conversation = initialize_conversation()
    introduction = get_chat_completions(conversation).content
    chat_gui.append({'bot':introduction})
    top_3_laptops = None
    return redirect(url_for('default_func'))

# Create a API that can be called directly to create product mapping whenever there are new/ modified laptop data
# Though this API is ideally a 'POST' method candidate, but the 'GET' option is provided for ease of calling from browser
@app.route("/map", methods = ['POST', 'GET'])
def map_laptops():
    laptop_df= pd.read_csv('laptop_data.csv')
    ## Create a new column "laptop_feature" that contains the dictionary of the product features
    laptop_df['laptop_feature'] = laptop_df['Description'].apply(lambda x: product_map_layer(x))

    # Save (overwrite) the file for future reference
    laptop_df.to_csv("updated_laptop.csv", index=False, header = True, mode='w')
    return "The Mapped CSV file has been saved!"


# Create the API to continue conversation
@app.route("/chat", methods = ['POST'])
def converse():
    global chat_gui, conversation, top_3_laptops
    user_input = request.form["user_message"]

    # Check if user input pass moderation validation
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('exit_conv'))

    # Obtain response from LLM on User Input
    conversation.append({"role": "user", "content": user_input})
    chat_gui.append({'user':user_input})

    response_assistant = get_chat_completions(conversation)
    
    # Check if we have received values for all Laptop Specification Keys
    # If received, LLM calls the respective Function which can then be executed in the below code section

    if response_assistant.function_call:
    
        # print("Response Assistant:")
        # print(response_assistant)

        chat_gui.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
        
        function_name = response_assistant.function_call.name
        function_args = json.loads(response_assistant.function_call.arguments)
        
        # If function name suggested by LLM is correct, execute the corresponding function
        if function_name == 'compare_laptops_with_user':
            top_3_laptops = compare_laptops_with_user(function_args)
        else:
            return redirect(url_for('default_func'))    # Go back to default page if non-relevant function is called

        # Validate the top recommendations if those are having minimum score to be passed to User
        validated_reco = recommendation_validation(top_3_laptops)
        # print("Reco Count: " + str(len(validated_reco)))

        if len(validated_reco) == 0:
            chat_gui.append({'bot':"Sorry, we do not have laptops that match your requirements. Connecting you to a human expert. Please end this conversation."})
            return redirect(url_for('default_func'))

        # Send the info on the function call and function response to GPT
        conversation.append({"role": "assistant", "content": f""" {response_assistant}"""})
        conversation.append(
            {
                "role": "function",
                "name": function_name,
                "content": f""" These are the user's products: {validated_reco}""",
            }
        )
        
        # Pass the laptop recommendations to LLM to formulate a user friendly message
        recommendation = get_chat_completions(conversation)
        
        moderation = moderation_check(recommendation.content)
        if moderation == 'Flagged':
            return redirect(url_for('exit_conv'))

        # Pass the LLM recommendation to User
        conversation.append({"role": "assistant", "content": recommendation.content})
        chat_gui.append({'bot':recommendation.content})
    else:
        # Continue interacting with User to obtain all Specification Key requirements
        moderation = moderation_check(response_assistant.content)
        if moderation == 'Flagged':
            return redirect(url_for('exit_conv'))
        
        conversation.append({"role": "assistant", "content": response_assistant.content})
        chat_gui.append({'bot':response_assistant.content})
    
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0", port=5001) # Deploy the application in local Host