from __future__ import print_function

from urllib.request import urlopen
from urllib.parse import quote
import boto3
import html
import json
import re
import os



print('Loading function')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    features = []
    try:

        page = urlopen('https://aws.amazon.com/cloudfront/details/').read().decode('utf-8')
        clean = html.unescape(page)
    
        for type in ["Regional Edge Cache", "Edge Location"]:
            
            # yes, ugly. #AWSWishList API to give me a list of Cloudfront locations
            for descriptions in re.findall('<p><b>' + type + 's(?:\s?:\s?</b>\s?|</b>\s?:\s?)(.*?)</p>', clean):
                for description in descriptions.split(';'):
                    description = description.strip()
                    
                    count = 1
                    if re.match(r'.*?\(\d\)', description):
                        count = re.search(r'.*?\((\d)\)', description).group(1).strip()
                    
                    location = re.search(r'([^(]*)', description).group(0).strip()

                    # Fixup the string first    
                    address = quote(location.replace(' ', '+'))
                    
                    # This is only as accurate as the name given. For example, we know 'Oregon' is really in/near Umatilla, OR
                    details = urlopen('https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + os.environ['geoKey'] )
                    coordinates = json.loads(details.read().decode('utf-8'))['results'][0]['geometry']['location']
                    
                    feature = {"type": "Feature"}
                    feature["properties"] = {
                        "name": location,
                        "type": type,
                        "count": count
                    }
                    feature['geometry'] = {
                        "type": "Point",
                        "coordinates": [coordinates['lng'], coordinates['lat']]
                    }
    
                    features.append(feature)
    
        body =  json.dumps({ "type": "FeatureCollection", "features": features })
        
        response = s3.put_object(
            Bucket=os.environ['s3Bucket'], 
            Key=os.environ['s3Key'], 
            Body=body, 
            ContentType='application/json', 
            ACL='public-read'
        )

    except Exception as e:
        print(e)

    return "OK"

