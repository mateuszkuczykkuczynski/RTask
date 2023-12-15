As i gained some experience i will refactor whole task (just for fun to see how much my code improves by time).
------SOLUTION FOR RECRUITMENT TASK------

How to execute my code and test my solution: 
- First install all requirements from requirements.txt using this command:  pip install -r requirements.txt or pip3 install -r requirements.txt
- Next there is a several things that can be tested locally:
    - main.py file can be executed just by running it using any IDE. 
    - main.py contains two functions get_exchange_rates and validate_data. Details about both functions are included in main.py
    - commented print statements will show output from data stored in SQLite in terminal. Just uncomment them.
    - To test API type: uvicorn api:app --reload, into terminal. Then go to http://127.0.0.1:8000/docs to play with it. 
    - To run tests wrote API just type: pytest, into terminal.

Logic behind my solution:

So that is a hard part. To store any data into database function get_exchange_rates must be executed. Function takes three parameters: source, date_from, base_currency. Source is from which place we want to get our data 'freecurrencyapi' or 'ecb' (stands for European Central Bank). Date_from is day from which we want to get data. Base_currency is currency against which we want to get all rates. 
All those parameters (including rates of course) are stored into database. 
Unfortunately we can get only daily data so if we want all rates for EUR from last week, dates need to be provided into program. 
The good news are that program does not allow duplicates and data are consistent. Also, "freecurrencyapi" provides all data 365 days a year so there was no need to pass last available data for a weekend or other free days. But that solution is implemented when we are using "ecb", so for Saturdays we go back for last available data (Friday) the same for Sundays for any other free days. 

API do not trigger functions so if any currency convert has to be done FIRSTLY data has to be inserted by running main.py. Example data were inserted into exchange_rates.db.
Data validation also works after data are inserted into database using get_exchange_rates with correct dates.

Usage example:
If you want to convert EUR to USD from date 2022-10-18 using freecurrencyapi all you need to do is run get_exchange_rates twice. First time with those parameters ('freecurrencyapi', '2022-10-18', 'USD') and second time with those: ('freecurrencyapi', '2022-10-18', 'EUR').
After that you can easily play with conversion in API. 

Google Cloud Function:
example gcloud functions deploy command: 
gcloud functions deploy NAME --runtime python38 --trigger-http --allow-unauthenticated --entry-point app --set-env-vars="PORT=8080"

Explanation:
Replace NAME with preferred function name. The --runtime flag specifies the Python version to use (this case 3.8), and --trigger-http indicates that the function should be triggered via an HTTP request. The --allow-unauthenticated flag allows unauthenticated access to the function. The --entry-point flag specifies the name of the function that should be executed (in this case app). Finally, the --set-env-vars flag sets an environment variable that tells the function to use port 8080.

Enjoy using my program! 
