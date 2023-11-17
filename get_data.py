import requests

domain_head = "https://cycling.data.tfl.gov.uk/usage-stats/"
query = []

with open('data_files.txt') as f:
    for line in f.readlines():
        query.append(line.strip())

def getCSV(query):
    response = requests.get(domain_head+query)
    # Check if the request was successful
    if response.status_code == 200:
        # If successful, write the content of the response to a local file
        with open(query, 'wb') as file:
            file.write(response.content)
    else:
        # If the request was not successful, print the status code
        print(f'Failed to download the file. Status code: {response.status_code}')

for q in query:
    getCSV(q)


