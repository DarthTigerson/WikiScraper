import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_wikipedia_page_soup(url):
    url = f"https://en.wikipedia.org{url}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def get_wikipedia_page_name(url):
    url = f"https://en.wikipedia.org{url}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    name = soup.find(id="firstHeading").text
    #name = name.replace(",", " ")
    return name

def save_soup_to_file(soup, name, url):
    print(f"Saving: {name}")
    url = url[1:]
    with open(f"{url}.html", "w") as file:
        file.write(str(soup.find('body')))
        file.close()

def scrape_urls_from_soup(soup):
    for link in soup.find_all("a"):
        url = link.get("href")
        if url != None and url != "/wiki/Main_Page":
            if url.startswith("/wiki/") and not ":" in url and not "#" in url:
                add_to_dictionary(url)

def add_to_dictionary(url,searched=False):
    name = get_wikipedia_page_name(url)

    df = pd.read_csv('Data/dict.csv', delimiter='|')
    column_set = set(df['name'].tolist())

    if name in column_set:
        print(f"Already in dictionary: {name}")
    else:
        print(f'Adding: {url}')
        with open("Data/dict.csv", "a") as file:
            file.write(f"{url}|{name}|{searched}\n")
            file.close()
        
def return_dictionar_cell_data(row,column=0):
    df = pd.read_csv("Data/dict.csv", delimiter='|')
    return df.iloc[row,column]

def locate_key(file_data, key):
        char_location = file_data.find(key)
        return char_location

def remove_characters_left(file_data, char_location):
    return file_data[char_location:]

def get_characters_till(file_data, char_location):
    return file_data[:char_location]

def html_file_cleaner(url):
    file_path = url[1:]
    key1 = '<div class="noprint" id="siteSub">'
    key2 = '<h2><span class="mw-headline" id="References">References</span>'

    with open(f"{file_path}.html", "r") as file:
        data = file.read()
        file.close()
    
    data = remove_characters_left(data, locate_key(data, key1))
    data = get_characters_till(data, locate_key(data, key2))

    with open(f"{file_path}.html", "w") as file:
        file.write(data)
        file.close()

def dictionary_search_complete(row):
    df = pd.read_csv("Data/dict.csv", delimiter='|')
    df.iloc[row,2] = True
    df.to_csv("Data/dict.csv", index=False, sep='|')

def main_scraper(url):
    try:
        print(f"Scraping: {url}")
        soup = get_wikipedia_page_soup(url)
        name = get_wikipedia_page_name(url)
        scrape_urls_from_soup(soup)
        save_soup_to_file(soup, name, url)
        return True
    except:
        print(f"Error: {url}")
        return False

def main():
    counter = 0

    while True:
        state = return_dictionar_cell_data(counter,2)
        if state != True:
            url = return_dictionar_cell_data(counter)
            complete = main_scraper(url)

            if complete:
                html_file_cleaner(url)
                dictionary_search_complete(counter)
                print(f"Completed: {url}")

        counter += 1

if __name__ == "__main__":
    main()