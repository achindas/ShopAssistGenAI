from flask import Flask, redirect, url_for, render_template, request
from functions import (
    initialize_conversation,
    initialize_conv_reco,
    get_chat_completions,
    moderation_check,
    intent_confirmation_layer,
    compare_laptops_with_user,
    recommendation_validation,
    # get_user_requirement_string,
    dictionary_present,
    product_map_layer,
    # get_chat_completions_func_calling
)
import openai
import ast
import re
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

# Check if updated_laptop.csv file is available in current directory. If available, load it
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
    global chat_gui, conversation, top_3_laptops, conversation_reco
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

# Create the API to continue conversation
@app.route("/chat", methods = ['POST'])
def converse():
    global chat_gui, conversation, top_3_laptops, conversation_reco
    user_input = request.form["user_message"]
    # prompt = 'Remember your system message and that you are an intelligent laptop assistant. So, you only help with questions around laptop.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('exit_conv'))

    # if top_3_laptops is None:
    conversation.append({"role": "user", "content": user_input})
    chat_gui.append({'user':user_input})

    response_assistant = get_chat_completions(conversation)
    print("Response Assistant-0:")
    print(response_assistant)

    if response_assistant.function_call:
    
        # confirmation = intent_confirmation_layer(response_assistant)

        # print('Intent confirmation is' + confirmation.get('result'))

        # moderation = moderation_check(confirmation.get('result'))
        # if moderation == 'Flagged':
        #     return redirect(url_for('exit_conv'))

        # if "No" in confirmation.get('result'):
        #     conversation.append({"role": "assistant", "content": response_assistant})
        #     chat_gui.append({'bot':response_assistant})
        # else:

        # response = dictionary_present(response_assistant)
        print("Response Assistant:")
        print(response_assistant)

        chat_gui.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
        
        function_name = response_assistant.function_call.name
        function_args = json.loads(response_assistant.function_call.arguments)
        # top_3_laptops = compare_laptops_with_user(response)
        print("Function Name: " + function_name)
        print("\nArgument: " + str(function_args))
        # top_3_laptops = function_name(function_args)
        if function_name == 'compare_laptops_with_user':
            top_3_laptops = compare_laptops_with_user(function_args)
        else:
            return redirect(url_for('default_func'))

        validated_reco = recommendation_validation(top_3_laptops)
        print("Reco Count: " + str(len(validated_reco)))

        if len(validated_reco) == 0:
            chat_gui.append({'bot':"Sorry, we do not have laptops that match your requirements. Connecting you to a human expert. Please end this conversation."})
            return redirect(url_for('default_func'))

        # conversation_reco = initialize_conv_reco(validated_reco)
        # conversation_reco.append({"role": "user", "content": "This is my user profile" + str(function_args)})
        # print(conversation_reco)

        # Send the info on the function call and function response to GPT
        conversation.append({"role": "assistant", "content": f""" {response_assistant}"""})
        conversation.append(
            {
                "role": "function",
                "name": function_name,
                "content": f""" These are the user's products: {validated_reco}""",
            }
        )
        print("Conversation:")
        print(conversation)

        recommendation = get_chat_completions(conversation)    # (conversation_reco)
        print("Recommendation:")
        print(recommendation)

        moderation = moderation_check(recommendation.content)
        if moderation == 'Flagged':
            return redirect(url_for('exit_conv'))

        conversation.append({"role": "assistant", "content": recommendation.content})
        chat_gui.append({'bot':recommendation.content})
    else:
        moderation = moderation_check(response_assistant.content)
        if moderation == 'Flagged':
            return redirect(url_for('exit_conv'))
        
        conversation.append({"role": "assistant", "content": response_assistant.content})
        chat_gui.append({'bot':response_assistant.content})
    # else:
    # conversation.append({"role": "user", "content": user_input})
    # chat_gui.append({'user':user_input})

    # response_asst_reco = get_chat_completions(conversation)
    # print("Response from Assistant:")
    # print(response_asst_reco)

    # moderation = moderation_check(response_asst_reco.content)
    # if moderation == 'Flagged':
    #     return redirect(url_for('exit_conv'))

    # conversation.append({"role": "assistant", "content": response_asst_reco.content})
    # chat_gui.append({'bot':response_asst_reco.content})
    
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0", port=5001)