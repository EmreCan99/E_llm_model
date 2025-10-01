#%% imports

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import requests
import json
from typing import List
from IPython.display import Markdown, display, update_display

print("imported")

# %%
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')


if api_key and api_key.startswith('sk-proj-') and len(api_key)>10:
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? Please visit the troubleshooting notebook!")
    
MODEL = 'gpt-4o-mini'
openai = OpenAI()

# %% A class to represent a Webpage

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
# %%
link_system_prompt = "You are provided with a list of link from a webpage." \
    " Please decide which links are relevant for the brochure such as the links " \
    "about; about us, careers/jobs, our team etc. Also if there are posts or stories " \
    "in the website bring few recent posts. Ignore navigation related links. " \
    "Do not bring more then 5 links. Some links might be given as " \
    "relative links and you should respond in full http format as JSON as in this example: \n"
link_system_prompt += """
{
    "links":[
        {"type": "about page", "url": "https://full.url/an/example/about"},
        {"type": "careers page, "url": "https://another.full.url/an/example/career"},
        {"type": "posts", "url": ""https://another.full.url/an/example/story""}
    ]
}
"""

# %%
def get_links_user_prompt(website):
    user_prompt = f"Here is the links from the website of {website.url} \n"
    user_prompt += "Please decide which link are relative links and find the relevant links " \
    "to add in the brochure and if there any posts or stories add few of them too. Respond in full http url in a JSON format. \n"
    user_prompt += "Links: \n"
    user_prompt += "\n".join(website.links)
    return user_prompt
# %%
nat = Website("https://brainofnatalia.blogspot.com/")
print(get_links_user_prompt(nat))

# %%
def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role":"system", "content": link_system_prompt},
            {"role":"user", "content": get_links_user_prompt(website)},
        ],
        response_format = {"type": "json_object"}
    )
    results = response.choices[0].message.content
    return json.loads(results)

# %%
result = get_links("https://brainofnatalia.blogspot.com/")

# %% ---------------------------------

# %%
def get_all_the_details(url):
    website = Website(url)
    results = "Landing page:\n"
    results += website.get_contents()
    links = get_links(website.url)
    print("the selected links", links)
    for link in links["links"]:
        results += f"Website type: {link['type']} \n\n"
        results += Website(link["url"]).get_contents()
    return results

# %%
result = get_all_the_details("https://huggingface.co/")
# %%
system_prompt = "You are an assistant that analysis a list of relevant links from a company website " \
    "and provide a short brochure for the potention investors, recruits or anyone interested in this company." \
    "Provide also general inforamtion about the company. Respond in Markdown"

# %%
def get_brochure_user_propmt(company_name, url):
    user_prompt = f"you are looking at a company called {company_name}. \n"
    user_prompt += "here are the details about the landing page and the " \
    "contents of the relevant links in that website. Use these to create" \
    "a short brochure of this company in markdown\n"
    user_prompt += get_all_the_details(url)
    if len(user_prompt) < 5_000:
        print("user_prompt is short enough")
    else:
        user_prompt = user_prompt[:5_000]
        print("user_prompt is truncated")
    return user_prompt

        
# %%
get_brochure_user_propmt("huggingface", "https://huggingface.co/")
# %%
def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model = MODEL,
        messages = [
            {"role": "system", "content":system_prompt},
            {"role": "user", "content":get_brochure_user_propmt(company_name, url)}
        ])
    results = response.choices[0].message.content
    return Markdown(results)

# %%
sonuc = create_brochure("Huggingface", "https://huggingface.co/")
# %%
