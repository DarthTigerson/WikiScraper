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

def save_soup_to_file(soup, name):
    print(f"Saving: {name}")
    with open(f"Data/{name}.html", "w") as file:
        file.write(str(soup.find('body')))
        file.close()

def scrape_urls_from_soup(soup):
    for link in soup.find_all("a"):
        url = link.get("href")
        if url != None and url != "/wiki/Main_Page":
            if url.startswith("/wiki/") and not ":" in url and not "#" in url:
                add_to_dictionary(url)

def add_to_dictionary(url,searched=False):
    add = True
    name = get_wikipedia_page_name(url)

    df = pd.read_csv('Data/dict.csv', delimiter='|')
    column_list = df['name'].tolist()

    for single_list in column_list:
        if single_list == name:
            print(f'URL already in dictionary: {url}')
            add = False
            break

    if add == True:
        print(f'Adding: {url}')
        with open("Data/dict.csv", "a") as file:
            file.write(f"{url}|{name}|{searched}\n")
            file.close()
        
def return_dictionar_cell_data(row):
    df = pd.read_csv("Data/dict.csv", delimiter='|')
    return df.iloc[row,0]

def dictionary_search_complete(row):
    df = pd.read_csv("Data/dict.csv", delimiter='|')
    df.iloc[row,2] = True
    df.to_csv("Data/dict.csv", index=False)

def main_scraper(url):
    try:
        print(f"Scraping: {url}")
        soup = get_wikipedia_page_soup(url)
        name = get_wikipedia_page_name(url)
        scrape_urls_from_soup(soup)
        save_soup_to_file(soup, name)
        return True
    except:
        print(f"Error: {url}")
        return False


def main():
    counter = 0

    while True:
        url = return_dictionar_cell_data(counter)
        complete = main_scraper(url)

        if complete:
            dictionary_search_complete(counter)
            print(f"Completed: {url}")

        counter += 1

if __name__ == "__main__":
    main()