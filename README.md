# Parsing of real estates from Facebook Marketplace (using Selenium) #

<br>

## Description ##

The parser can parse real estate objects from Facebook Marketplace using Selenium and BeautifulSoup4 technology. Parsing collects the following information:
1. Title
2. Price
3. Address
4. Animal Friendly
5. Date of publication
6. Description
7. Object URL
8. Rating
9. Date of author registration
10. Chat to Author URL
11. Date of parsing
12. Relevance
13. Images

You can also flexibly customize the filtering system for real estate objects using custom configurations for the parser. By default, the parser will write the received data to a Google Sheet. However, you can easily change this behavior if you need to.

<br>

## Quick Start ##

1. Download the git repository on your computer
2. Download all requirements from <b> requirements.txt </b>
3. Download <a href="https://chromedriver.chromium.org/downloads">chromedriver</a> in project directory and Google Chrome for your OS (Chromedriver must be compatible with your version of Chrome)
4. Create your service account from <a href="https://cloud.google.com/gcp/">Google Cloud Platform</a> and Google Sheet
5. Input your configurations in <b> config.py </b>
6. Run script <b> main.py </b>
7. Enjoy!)

<br>

## Create a Google Sheet ##

Parser write final result in Google Sheet. 
<br>
You google sheet should have the following structure:
<br>
<table>
    <tr>
        <td>A</td> <td>B</td> <td>C</td> <td>D</td> <td>E</td> <td>F</td> <td>G</td> <td>H</td> <td>I</td> <td>J</td> <td>K</td> <td>L</td> <td>M</td> <td>N</td> <td>O</td>
    </tr>
    <tr>
        <td>Title</td> <td>Price</td> <td>Address</td> <td>Animal Friendly</td> <td>Date of publication</td> <td>Description</td> <td>Object URL</td> <td>Rating</td> <td>Date of author registration</td> <td>Chat to Author URL</td> <td>Date of parsing</td> <td>Place ID</td> <td>Relevance</td> <td>Main Image</td> <td>Images</td>
    </tr>
</table>

<br>

## Install requirements ##

To install all requirements you must open terminal and in project directory input next command
    
    pip3 install -r requirements.txt

For Windows:
    
    pip install -r requirements.txt

<br>

## Set your configurations ##

In file <b> config.py </b> you can set all your configurations

Your facebook account credentials

    facebook_login = ""
    facebook_password = ""

Your Google Sheet parameters

    google_sheet_id = ""
    page_name ""

Your filter parameters

    keywords = [] 
    city_code = ''  
    limit_of_pages_from_one_run = 1
    filter_words = []


Your service account api_json

    api_json = {}


Select headless mode:

    headless_mode = True

<br>


## Save images ##

The script automated save images. But if you want to run the script on server you must input "<b>root_server_image_url</b>" configuration.
If you run the script on local computer, set this configuration:

    root_server_image_url = ""

<br>

## Check the relevance of objects ##

If you use the parser and your Google Sheet has accumulated a lot of records, then you most likely encountered a problem of their relevance.
<br>
That is why an additional functionality was added to the parser - checking the relevance of objects.
<br>
If you want to check the relevance of objects you must run "<b>check_the_relevance_of_objects.py</b>". This script check all objects in Google Sheet and rewrite field "Relevance"

<br>

## Important! ##

The html structure of the Facebook Marketplace page may change. This is necessary to change classes and search selectors. The structure of the parser does not come from this, but may require some manual changes to the code. Especially for this, I tried to make the code easy to read and easy to maintain. If you have any questions about the code and its implementation, write to me on Telegram
