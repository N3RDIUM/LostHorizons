import requests
import pandas as pd
url_base = 'http://ec2-3-108-196-161.ap-south-1.compute.amazonaws.com/profile?id='
max_n = 100
def create_url(n):
    return f"{url_base}{n}"

results = {}

for n in range(max_n):
    res = requests.get(create_url(n))
    if res.status_code == 200:
        print(f"I got a profile at {create_url(n)}!")
        results[n] = create_url(n)
        
# Save results to CSV
header = [['id', 'url']]
data = []
for i in results:
    data.append([i, results[i]])
to_write = header + data
with open('results.csv', 'w') as f:
    pd.DataFrame(to_write).to_csv(f, header=False, index=False)