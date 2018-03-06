from urllib import request, parse
from bs4 import BeautifulSoup
import csv

errors_csv = open('errors.csv','w')
errors_wr = csv.writer(errors_csv, lineterminator='\n', delimiter=',', escapechar='\\', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
errors_wr.writerow([
    'center_id',
    'url'
])

centers_csv = open('centers.csv', 'w')

centers_wr = csv.writer(centers_csv, lineterminator='\n', delimiter=',', escapechar='\\', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
centers_wr.writerow([
    'id',
    'name',
    'url',
    'address',
    'facility_type',
    'license_type',
    'capacity',
    'ages'
])

inspections_cv = open('inspections.csv', 'w')
inspections_wr = csv.writer(inspections_cv, lineterminator='\n', delimiter=',', escapechar='\\', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
inspections_wr.writerow([
    'center_id',
    'date',
    'complaint_related',
    'violations',
    'standard_numbers'
])

url = 'http://www.dss.virginia.gov/facility/search/cc2.cgi'

data = parse.urlencode({'search_require_client_code-2101' : '1',
                         'search_require_client_code-2106'  : '1',
                         'rm':'Search'}).encode()
req =  request.Request(url, data=data) # this will make the method "POST"
# resp = request.urlopen(req)

resp = open('search_results.html','r')

soup = BeautifulSoup(resp, 'html.parser')
results_table = soup.find(id="pagenatedlic")
centers = results_table.find_all('a')

for i, c in enumerate(centers):
    facility_type = ''
    license_type = ''
    capacity = ''
    ages = ''
    center_id = i+1
    name = c.get_text()
    center_url = c['href']
    center_url = 'http://www.dss.virginia.gov' + center_url

    address = c.find_parent('td').find_next_sibling('td')
    if address is None:
        address = ''
    address = ''.join(string.strip() for string in address.stripped_strings)
    address = address.replace('\\n','').replace('\\t','')
    # print(address.rstrip().lstrip() + '\n')
    # continue

    center_req =  request.Request(center_url)
    center_resp = request.urlopen(center_req)
    center_soup = BeautifulSoup(center_resp, 'html.parser')

    rows = center_soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele for ele in cols]
        for ele in cols:
            value = ele.find_next_sibling('td')
            if 'Facility Type' in ele.text:
                facility_type = ''.join(string for string in value.stripped_strings)
            if 'License Type' in ele.text:
                license_type = ''.join(string for string in value.stripped_strings)
            if 'Ages' in ele.text:
                ages = ''.join(string for string in value.stripped_strings)
                ages = ages.replace('\n','').replace('\t','').replace('\r','')
            if 'Capacity' in ele.text:
                capacity = ''.join(string for string in value.stripped_strings)
                
    centers_row = [center_id,name,center_url,address,facility_type,license_type,capacity,ages]
    print(centers_row)
    centers_wr.writerow(centers_row)

    # Inspections
    inspections = center_soup.find_all('td', string='Inspection Date')
    for inspection in inspections:
        inspection_rows = inspection.find_all_next('a')
        for report in inspection_rows:
                parent = report.find_parent('tr')
                if parent is None:
                    continue
                cols = parent.find_all('td')
                if len(cols) < 4:
                    continue
                
                inspection_date = ''.join(string for string in cols[0].stripped_strings)
                complaint_related = ''.join(string for string in cols[2].stripped_strings)
                violations = ''.join(string for string in cols[3].stripped_strings)
                standard_numbers = []
                # print(cols)
                report_url = report['href']
                if 'Inspection' in report_url:
                    report_req =  request.Request(url + report_url)
                    try:
                        report_resp = request.urlopen(report_req, timeout=3)
                    except:
                        print('Error retrieving ' + url + report_url)
                        errors_wr.writerow([center_id,center_url])
                        continue
                    report_soup = BeautifulSoup(report_resp, 'html.parser')
                    violations_anchor = report_soup.find('a',attrs={'name':'Violations'})
                    if violations_anchor is None:
                        continue
                    table_rows = violations_anchor.find_all_next('tr')
                    for row in table_rows:
                        divisions = row.find_all_next('td')
                        for div in divisions:
                            if 'Standard #:' in div.text:
                                standard = div.find_next('td')
                                standard = ''.join(string for string in standard.stripped_strings)
                                standard_numbers.append(standard)
                
                    standard_numbers = '; '.join(standard_numbers)
                    inspection_row = [center_id,inspection_date,complaint_related,violations,standard_numbers]
                    inspections_wr.writerow(inspection_row)
                    print(inspection_row)
                
