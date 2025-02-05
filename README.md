# **Laptop Shopping Assistant - Using OpenAI & Flask**

## **Table of Contents**
* [Introduction](#introduction)
* [Problem Statement](#problem-statement)
* [Application Functionalities](#application-functionalities)
* [Application Architecture](#application-architecture)
* [Major Functions](#major-functions)
* [Technologies Used](#technologies-used)
* [Conclusion](#conclusion)
* [Acknowledgements](#acknowledgements)

---

## **Introduction**
With the rapid growth of eCommerce, customers often face challenges in selecting the right product that meets their specific requirements. **Shop Assistance Chatbots** are becoming increasingly popular as they help users navigate vast product catalogs, filter options based on personalized preferences, and make informed purchasing decisions. A well-designed chatbot ensures that customers receive tailored recommendations, reducing decision fatigue and improving user satisfaction. 

The **Laptop Shop Assistant Chatbot** guides users through a series of questions to understand their needs in terms of **GPU intensity, display quality, portability, multitasking, processing speed, and budget**. Once all specifications are gathered, it intelligently matches the requirements with the best available laptops from the catalog and provides recommendations. This intelligent chatbot enhances the shopping experience by providing **accurate, fast, and structured responses** to user queries, making it a valuable tool in the online retail industry.

---

## **Problem Statement**
Traditional rule-based chatbots rely on hardcoded conditions and decision trees, which often lead to **rigid and unnatural interactions**. Users must provide structured responses to predefined questions, and the chatbot may struggle with variations in input. This results in a poor user experience, reduced engagement, and an inability to handle complex queries dynamically.

To address this, we utilized **OpenAI’s Function Calling API**, which enables the chatbot to intelligently determine when and how to call specific backend functions. This approach enhances:
- **Performance**: By invoking functions only when necessary, redundant computations are minimized.
- **Conversation Flow**: The chatbot interacts dynamically, guiding users seamlessly through the recommendation process without requiring predefined input formats.
- **User Experience**: The assistant understands free-form responses, making the interaction more natural and adaptive.

By leveraging this function calling mechanism, the chatbot can intelligently decide when to fetch laptop data, validate user preferences, compare options, and present recommendations. This makes the chatbot **efficient, responsive, and highly scalable** for a wide range of eCommerce applications.

---

## **Application Functionalities**

The **Laptop Shop Assistant Chatbot** includes the following key functionalities:

1. **User Interaction and Query Understanding**

    * The chatbot starts by engaging with the user to gather details about their laptop needs.
    * It progressively asks about key specifications such as performance, budget, and usability factors.
    
2. **OpenAI Function Calling for Structured Execution**

    * Instead of relying on multiple calls to ChatCompletion API to confirm the user requirements, OpenAI’s `Function Calling mechanism` is used to dynamically trigger the relevant function when all necessary specifications are gathered.
    * This reduces inconsistencies and simplifies the conversation flow.

3. **Laptop Matching and Recommendation**

    * The chatbot maps product descriptions to structured specifications using ChatCompletion APIs.
    * The specifications are stored in persistent data storage in `updated_laptop.csv` for quick lookups.
    * It filters laptops from this catalog based on user requirements. 
    * The top 3 laptops with the best match scores are recommended.

4. **Moderation and Response Refinement**

    * OpenAI’s `moderation API` is used to ensure that inappropriate queries are flagged.
    * Final laptop recommendations are validated before being presented to the user.

---

## **Application Architecture**

The **Laptop Shop Assistant** Chatbot follows a **web-based client-server architecture** using Python and Flask. The client-side consists of a web interface where users interact with the chatbot by specifying their laptop preferences. These inputs are sent to the Flask-based server, which processes the user requests, extracts relevant requirements, and invokes OpenAI’s APIs to determine the next steps dynamically. The server then retrieves laptop specifications from a structured dataset, applies filtering logic, and generates personalized recommendations. The response is sent back to the client. This architecture enables a **scalable, lightweight, and efficient** chatbot.

![Architecture Diagram](images/Architecture%20Diagram.png)

![Application Workflow](images/App%20Workflow.png)


---

## **Major Functions**
### **1. `initialize_conversation()`**
This function provides the detailed guideline for LLM model to interact and infer user inputs through careful system prompts

### **2. `get_chat_completions()`**
It receives the on-going conversation history including the last input from user and returns the response by Assistant. Within this function, the Assistant determines when to trigger defined Functions based on collection of parameter values.

### **3. `moderation_check()`**
This function ensures that user inputs adhere to safe and meaningful queries by leveraging OpenAI’s moderation API. If inappropriate queries are detected, it ends the conversation.

### **4. `product_map_layer()`**
This function maps raw product descriptions into structured specifications, enabling efficient filtering and comparison during recommendation.

### **5. `compare_laptops_with_user()`**
This function compares available laptops against the user’s specified requirements (budget, performance, screen size, etc.) and ranks the best matches. It filters out unsuitable options and presents the top recommendations.

### **6. `recommendation_validation()`**
Once all inputs are gathered, this function validates the top laptop matches based on a weighted scoring system. The chatbot then presents the recommendations in a user-friendly format.

### **7. `/chat API - converse()`**
This function implements the `/chat` API which essentially maintains the conversation with User, identifies relevant constraints from user responses, such as **preferred processor type, screen resolution, GPU needs, and price range**, ensuring accurate product recommendations.

### **8. `/map API - map_laptops()`**
This function implements `/map` API that can be called directly to create product mapping whenever there are new/ modified laptop data.

### **Application Snapshots**

![Application Snapshots](images/App%20Snapshots.png)

---

## **Technologies Used**
The chatbot is built using the following technologies:
- **Python** – Core programming language
- **Flask** – Web framework for hosting the chatbot interface
- **OpenAI GPT-3.5 Turbo** – For natural language understanding and function calling
- **Pandas** – For handling and processing laptop data
- **Tenacity** – For API call retry mechanisms
- **CSV (updated_laptop.csv)** – Storage format for laptop specifications

---

## **Conclusion**
The **Laptop Shop Assistant Chatbot** effectively utilizes **OpenAI’s Function Calling API**, transforming the way users interact with AI-powered shopping assistants. 

* **Improved interaction consistency:** Function Calling mechanism ensures a structured flow of information.
* **Better user experience:** The chatbot guides users systematically instead of relying on unstructured inputs.
* **Accurate recommendations:** NLP-based product mapping enhances the laptop selection process.
* **Scalability:** The system can easily be expanded to include new laptop models with updated specifications.

The result is an **intelligent, user-friendly, and efficient** assistant that significantly enhances the laptop shopping experience.

---

## **Acknowledgements**

This case study has been developed as part of Post Graduate Diploma Program on Machine Learning and AI, offered jointly by Indian Institute of Information Technology, Bangalore (IIIT-B) and upGrad.
