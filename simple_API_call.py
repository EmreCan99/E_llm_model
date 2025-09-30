
#%% imports

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
print("imported")

#%% the API Key
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

#%%

system_prompt = "You are an assistant that reads the given Turkish text\
and provides one sentence summary of the given text and find if there are\
any word with more than 3 suffixes and list them at the end. Ignore the \
markdown formating symbols if the the given text contains. Respond in markdown."

def user_prompt(text):
    prompt = f"You are looking at a text given in Turkish; \n{text}.\n"
    prompt += "Please provide one sentence summary and if there are words \
with more than three suffixes list them at the end in markdown."
    
    return prompt

# %%

def messages_for(text):
    message = [
            {"role":"system", "content":system_prompt},
            {"role":"user", "content": user_prompt(text)}
        ]
    return message

#%%
openai = OpenAI()

# %%

def ozetle(text):
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(text)
    )
    return response


#%%

text = """
Oktay Anar'ın ikinci kitabı._
3 nesil hiyelkarın hikayesini yaklaşık 150 yıllık bir süreyi anlatıyor. İlk hiyelkar mekanik öğrenerek padişaha savaş makineleri yapmaya çalışıp epey de başarılı oluyordu ancak bürokraside kaybolup hiçbir icadını kullandırtamadı. Evlatlık aldığı iri yarı filistinli çocuk çok daha saldırgan şekilde icatları ile güç ve iktidar kazanmaya çalıştı çok daha az başarılıydı. Onun beynini yıkamak ve neslini devam ettirmek için evlatlık aldığı çocuk ise hiyle kullanmak yerine bilime daha fazla kayması gerktiğini fark etti.
Kitabın sonunda ***3 tane*** “kör” kelimesiyle ilgili anlatılan çok güzel kısa hikaye vardı. Bu hikayelerden birinde Osmanlıcada kör kelimesi ile göz kelimesi arasında tek bir nokta olduğunu fark ettirdi ve önceki iki neslin yaptığı tahayyülün noktasız olduğu ve hiyle yapmaktan türeyen bir kelime olduğunu ancak zihninde tek bir noktadan başka bir şey göremeyecek kadar hafızasını kaybeden evlatlığın artık noktalı olan tahayyülü, yani hayal etmekten türeyen tahayyülü ettiğini yani bir nevi bilimsel düşünceyi bulduğunu gördük.
Kitapta, özellikle baş kısımlarında, çok güzel mekanik çizimleri var.
"""

özet = ozetle(text)
# %%
display(Markdown(özet.choices[0].message.content))
