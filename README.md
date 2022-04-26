# AI_gen_specs


*Description of each files*
1. ebay_batch_scrapper.py 
- Since ebay only allow 10 pages in one scrape, we break it down into sections in term of pricing
- e.g. we filter the search from price $5 to $10 in the first scrape, and iterate the scraping process with $5 increments
- Some examples of scrape result can be found "outputs\ebay" and "heater_data" ,which will then be concetenate with other date and store in "data"

2. product_review.ipynb
- Extract feature description 
- Extract reviews

3. youtube_api.py
- This is a youtube scraper class based on search terms 
- We input the search term in the Youtube_api.search call in the main function 
- In this case we use heater_product as our search term
- The extracted data is stored in a pkl file, combined_data.pkl in support/combined_data.pkl folder

4. api.ipynb 
- questions to texture data
- extract keywords 
- summarization for qualitative data

5. graph_dependancy.ipynb
- Concatenate all reviews from all sources (youtube, ebay, productreviews
- Identify with keywords are mentioned the most
- Sentiment Analysis
- Graph dependency
- OpenAI keywords extraction and summarization
- Getting product specification

6. ML_Model_Spec.ipynb
- This is the jupyter notebook used to run the ML Model Classifier
- 4 models are used in this file: Logistic Regression, RandomForestClassifier, Extra Trees Regressor and SGD Classifier 
- It extracts data from the folder heater_data which contains the data scraped from ebay