# Parsing of real estates from Facebook Marketplace (using Selenium) #

## Quick Start ##
1. Download the git repository on your computer
2. Download all requirements from <b> requirements.txt </b>
3. Download <a href="https://chromedriver.chromium.org/downloads">chromedriver</a> in project directory and Google Chrome for your OS (Chromedriver must be compatible with your version of Chrome)
4. Create your service account from <a href="https://cloud.google.com/gcp/">Google Cloud Platform</a> and Google Sheet
5. Input your configurations in <b> config.py </b>
6. Run script <b> main.py </b>
7. Enjoy!)


## Create a Google Sheet ##
Parser write final result in Google Sheet. 
<br>
You google sheet should have the following structure:
<br>
<table>
    <tr>
        <td>A</td> <td>B</td> <td>C</td> <td>D</td> <td>E</td> <td>F</td> <td>G</td> <td>H</td> <td>I</td> <td>J</td> <td>K</td>
    </tr>
    <tr>
        <td>Title</td> <td>Price</td> <td>Address</td> <td>Animal Friendly</td> <td>Date of publication</td> <td>Description</td> <td>Object url</td> <td>Rating</td> <td>Date of author registration</td> <td>Date of parsing</td> <td>Place ID</td>
    </tr>
</table>


## Install requirements ##
To install all requirements you must open terminal and in project directory input next command
    
    pip3 install -r requirements.txt

For Windows:
    
    pip install -r requirements.txt


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


## Important! ##
The html structure of the Facebook Marketplace page may change. This is necessary to change classes and search selectors. The structure of the parser does not come from this, but may require some manual changes to the code. Especially for this, I tried to make the code easy to read and easy to maintain. If you have any questions about the code and its implementation, write to me on Telegram