# Edgar Scrape - Warn Act

### Description
The goal of this project was to see if companies were complying with the Worker Adjustment and Retraining Notification Act of 1988's (WARN Act) reporting requirements. My role in the project was to find all companies that had reported a layoff to the SEC via an 8-k.

### How it works
1. I gathered a list of all possible CIKs in Edgar to insure our dataset was complete.
2. A list of terms related to layoffs was created to search against.
3. I wrote a Python script to retrieve all 8-k's (as a txt document) for each company in Edgar
4. Each 8-k was searched against the key words previously determined.
5. If a match was found, the result was exported to a spreadsheet.
