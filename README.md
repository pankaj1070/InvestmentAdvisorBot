# InvestmentAdvisorBot

![Chatbot](Images/Chatbot.jfif)


**Objective:**

Create an investment advisor bot which can advise clients on different Portfolios based on their risk appetite and calculate the expected returns using machine learning over a period of time. The Portfolios include US equity martket index, Bloomberg bond index and Bitcoin. Since machine learning and automated trading are disrupting finance to improve customer experience. This would be a great way to reach and engage with young people.

Project Overview:

**Portfolio Creation in Sagemaker:** Defined a Portfolio using data from yahoo finance and generated signals using various Machine learning models.

**Invoking endpoints from lambda function:** The Signals generated from Machine learning Models were generated through invoking Sagemaker endpoints through lambda function.

**Creation of Amazon Lex robo advisor:** Defined an Amazon Lex bot with a single intent that establishes a conversation about the requirements to suggest an investment portfolio to clients.

**Enhance the Robo Advisor with an Amazon Lambda Function:** Created an Amazon Lambda function that validates the user's input and returns the investment portfolio recommendation with expected returns. This task includes testing the Amazon Lambda function and making the integration with the bot.







