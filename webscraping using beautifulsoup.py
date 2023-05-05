from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import threading


def scrape_course_info(obj):
    # Extract information for a single course
    a_href = obj.find("a", {"class": "course-card__wrapper"}).get("href")
    a_href = "https://maktabkhooneh.org" + a_href
    a1 = requests.get(a_href).text
    soup1 = BeautifulSoup(a1, "lxml")
    comment = soup1.find("div", class_="comments__desc-user top-margin")
    if comment == None:
        comment = "None"
    else:
        comment = comment.text
    name = obj.find("div", class_="course-card__title")
    if name == None:
        name = obj.find("div", class_="course-card__title--career").text
    else:
        name = name.text
    price_section = obj.find("div", class_="course-card__price")
    if price_section == None:
        price = "None"
    else:
        price_section = price_section.find(text=True, recursive=False)
        price = price_section
        price = re.search(r'\d{1,3}(,\d{3})*', price).group()
    return (name, price, comment)


html_text = requests.get('https://maktabkhooneh.org/learn/python/').text
soup = BeautifulSoup(html_text, "lxml")
objs = soup.find_all(
    "div", class_="side-margin bottom-margin js-filter-item active-item")

# Create empty lists to store course information
course_names = []
course_prices = []
course_comments = []

# Define a worker function for each thread


def worker(objs_slice):
    for obj in objs_slice:
        name, price, comment = scrape_course_info(obj)
        course_names.append(name)
        course_prices.append(price)
        course_comments.append(comment)


# Split the list of objects into several chunks
n_threads = 4
chunk_size = len(objs) // n_threads
obj_chunks = [objs[i:i+chunk_size] for i in range(0, len(objs), chunk_size)]

# Start a thread for each chunk
threads = []
for chunk in obj_chunks:
    t = threading.Thread(target=worker, args=(chunk,))
    t.start()
    threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()

# Create a Pandas DataFrame with the course information
df = pd.DataFrame({
    'course_name': course_names,
    'price': course_prices,
    'comment': course_comments
})

# Print the DataFrame
print(df)
