# Job Tracker

This project sources jobs from various job boards to recommend jobs to users based on their preferences. This project arose from the need to automate job searches and filter out irrelevant jobs during my internship search and scores jobs to find the most relevant jobs according to many criteria.


## How to run

Clone the repository and change directory into the project directory.

Ensure that all dependencies are installed by executing 
`pip install -r requirements.txt`

Run main.py by executing 
`python main.py` 
on the terminal in the project's root directory.


## Project Structure

1. pages - It contains all non-root pages of the webapp made using Taipy. There's also a stylesheet for the jobs.py file.

2. src - Contains most of the code for this tool. The scrapers are stored in the scrapers directory, only grab_indeed.py and yc.py are used for now. The processing.py and aggregate.py files are for processing and aggregation of data respectively.

3. Other files present in the root dir - main.py contains code for the root page of the multi page taipy app, others are irrelevant to the normal functioning of the tool(except requirements.txt and README.md).

A video demonstration of some of the features of this app is available [here](https://drive.google.com/file/d/1c0blZZL1eIHh5n8_6OFFAVL34rNM6wwm/view?usp=sharing).

## Implemented features - 
- Scrapers for indeed and ycombinator - gets jobs using Selenium and BeautifulSoup.
- Crawlers for getting job descriptions of the jobs scraped. 
- Processing pipelines - scripts to modify the raw data to make meaningful recommendations. Currently implemented in python using domain knowledge.
- A user interface implemented in Taipy, to show and filter the ranked jobs.

## Future Enhancements - 
- Improve the description processing pipeline, connect all the scripts using Airflow pipelines.
- Implement better scoring methods such as the BM25 model, along with some query generation mechanism.
- Gather user feedback on each job card (through upvote and downvote buttons) to affect the job's ranking - this way incorrect rankings may get corrected, also paves the way for model weights to stay relevant with drift.