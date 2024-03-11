import sys
import json
import lxml.html
import requests
import pandas as pd
import pprint

def scrape_internship_page(url):
    iop_dict = {'url': url}

    response = requests.get(url)
    elem = lxml.html.fromstring(response.text)

    title_block = elem.cssselect('div.interiorIntro h2.interiorIntro-title')
    iop_dict['name'] = title_block[0].text_content().strip()

    deadline_element = elem.cssselect('span.cardSingle-item-heading:contains\
                                      ("Application Deadline") + \
                                      span.cardSingle-item-description.\
                                      cardSingle-item-description--alt')

    if deadline_element:
        iop_dict["Deadline"] = deadline_element[0].text_content().strip()
    else:
        iop_dict["Deadline"] = ""

    a_element = elem.cssselect('a.simpleNav-link')

    if a_element:
        iop_dict['Link to apply'] = a_element[0].get('href')
    else:
        iop_dict['Link to apply'] = ""

    try:
        text_block = elem.xpath('//p[strong[contains(text(), \
                                "Responsibilities:")]]')[0]
        responsibilities_text = ''.join\
            (text_block.xpath('descendant::text()\
                              [preceding-sibling::strong[contains(text(), \
                            "Responsibilities:")]]'))
        iop_dict['Responsibilities'] = responsibilities_text[:300]
    except:
        iop_dict['Responsibilities'] = ""

    return iop_dict

def get_page_urls(url):
    response = requests.get(url)
    elem = lxml.html.fromstring(response.text)
    links = elem.cssselect('a.cardDetails-button')
    href_list = [link.get('href') for link in links]
    return href_list

def get_next_page_url(url):
    response = requests.get(url)
    elem = lxml.html.fromstring(response.text)
    node = elem.get_element_by_id("page:next")

    if node:
        page_value = node.get('s-val:page')
        generated_url = f"https://politics.uchicago.edu/internships-careers/\
            internship-hub?page={page_value}&sort=asc&view=grid"
        return generated_url

    return None

def crawl(max_internships_to_crawl):
    list_page_url = "https://politics.uchicago.edu/internships-careers\
        /internship-hub"
    internships = []
    urls_visited = 0

    while urls_visited <= max_internships_to_crawl:
        page_urls = get_page_urls(list_page_url)
        
        for url in page_urls:
            internships.append(scrape_internship_page(url))
            urls_visited += 1

        list_page_url = get_next_page_url(list_page_url)
        
        if list_page_url is None:
            break

    df = pd.DataFrame(internships)
    df.to_excel("internships.xlsx", index=False)
    
    with open("internships.json", "w") as f:
        json.dump(internships, f, indent=1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m crawler <url>")
        sys.exit(1)
    result = scrape_internship_page(sys.argv[1])
    pprint(result)
