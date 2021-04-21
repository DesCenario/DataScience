import math
import os
import pickle
from urllib.parse import unquote

import geocoder
import simplekml
import twitter
# TWITTER API
from cluster import KMeansClustering
from cluster.util import centroid
from geopy import geocoders

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
AUTHENTICATION = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
TWITTER_API = twitter.Twitter(auth=AUTHENTICATION)

# GEOPY API
GOOGLEMAPS_APP_KEY = ''
GOOGLE_GEOPY = geocoders.GoogleV3(api_key=GOOGLEMAPS_APP_KEY)

K_ALL = 10
COUNTRIES = [
    {'name': 'Switzerland', 'id': 23424957, 'area': 41285, 'k': 3},
    {'name': 'Germany', 'id': 23424829, 'area': 357582, 'k': 5},
    {'name': 'France', 'id': 23424819, 'area': 632834, 'k': 5},
    {'name': 'Austria', 'id': 23424750, 'area': 83882, 'k': 4},
    {'name': 'Italy', 'id': 23424853, 'area': 301338, 'k': 3},
]

LONGITUDE_MAX_DEVIATION = 8
LATITUDE_MAX_DEVIATION = 8

CALL_LIMIT = 180
TOPIC_LIMIT = 200

TOPIC_AMOUNT_PER_COUNTRY = 4
COUNT_TWEETS = 100
TWEETS_PER_TOPIC = 200

TOPICS_PICKLE_FILE = 'topics.pkl'
STATUSES_PICKLE_FILE = 'statuses.pkl'
COORDINATES_PICKLE_FILE = 'coordinates.pkl'


def get_top_50_trending_topics(place_id):
    topics = TWITTER_API.trends.place(_id=place_id)
    trends = topics[0]['trends']
    queries = list(map(lambda trend: trend['query'], trends))
    return queries


def search_statuses_with_geocode_by_query(tweet_id, country_coordinates):
    geocode = '{0},{1},{2}'.format(
        country_coordinates['latitude'],
        country_coordinates['longitude'],
        str(country_coordinates['radius']) + 'km')

    search_result = TWITTER_API.search.tweets(
        q=tweet_id,
        include_entities=False,
        count=COUNT_TWEETS,
        geocode=geocode)
    statuses = search_result["statuses"]
    for tweet in range(int(TWEETS_PER_TOPIC / COUNT_TWEETS) - 1):
        try:
            next_results = search_result['search_metadata']['next_results']
        except KeyError as e:
            break

        kwargs = dict([kv.split('=') for kv in unquote(next_results[1:]).split("&")])

        search_result = TWITTER_API.search.tweets(**kwargs)
        statuses += search_result['statuses']
    return statuses


def get_coordinates_for_place_from_arcgis(origin, place):
    location = geocoder.arcgis(place)

    if len(location.geojson['features']) < 1:
        return None

    latitude = location.geojson['features'][0]['properties']['lat']
    longitude = location.geojson['features'][0]['properties']['lng']
    address = location.location

    if location is not None:
        return {'origin': origin,
                'longitude': longitude,
                'latitude': latitude,
                'address': address}
    else:
        return None


def get_coordinates(status, country_coordinates):
    if status['coordinates'] is not None:
        return {'origin': 'coordinates',
                'latitude': status['coordinates']['coordinates'][1],
                'longitude': status['coordinates']['coordinates'][0],
                'address': status['place']['full_name']}
    if status['place'] is not None:
        return get_coordinates_for_place_from_arcgis('place', status['place']['full_name'])
    if status['user']['location'] != '':
        location = get_coordinates_for_place_from_arcgis('user', status['user']['location'])
        if location is None:
            return None

        if abs(location['longitude'] - country_coordinates['longitude']) < 0.2 or abs(location['latitude'] - country_coordinates['latitude']) < 0.2:
            return None

        if abs(location['longitude'] - country_coordinates['longitude']) > LONGITUDE_MAX_DEVIATION or abs(location['latitude'] - country_coordinates['latitude']) > LONGITUDE_MAX_DEVIATION:
            return None

        return location
    return None


def save_pickle(filename, statuses):
    with open(filename, 'wb') as file:
        pickle.dump(statuses, file)


def load_pickle(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def pickle_exists(filename):
    return os.path.isfile(filename)


def get_statuses_from_topics_per_country(topics_per_country):
    statuses = []
    for statuslist in list(map(lambda status_list: status_list['statuses'], topics_per_country)):
        statuses.extend(statuslist)

    return statuses


def get_coordinates_from_coordinates_per_topic_for_country(coordinates_per_topic, country):
    coordinates = []
    for coordinatelist in list(filter(lambda coords: country in coords['country'], coordinates_per_topic)):
        if len(coordinatelist['statuses']) > 200:
            cupped_statuses = coordinatelist['statuses'][:200]
            coordinatelist['statuses'] = cupped_statuses
        coordinates.append(coordinatelist)
    return coordinates


def save_all_coordinates(coordinates_per_topic, name):
    kml = simplekml.Kml()

    for coordinate in coordinates_per_topic:
        for status in coordinate['statuses']:
            if status['coordinates']['longitude'] < 0 or status['coordinates']['latitude'] < 0:
                continue

            kml.newpoint(
                name=unquote(coordinate['topic']),
                coords=[(status['coordinates']['longitude'], status['coordinates']['latitude'])])

    kml.save('{}_{}.kml'.format('all', name))


def save_kmeans_coordinates(coordinates_per_topic, name, k):
    K = k

    coordinates = []
    for coordinate in coordinates_per_topic:
        for status in coordinate['statuses']:
            if status['coordinates']['longitude'] < 0 or status['coordinates']['latitude'] < 0:
                continue

            coordinates.append((status['coordinates']['longitude'], status['coordinates']['latitude']))

    cl = KMeansClustering(coordinates)
    centroids = [centroid(c) for c in cl.getclusters(K)]

    kml = simplekml.Kml()
    for i, c in enumerate(centroids):
        kml.newpoint(
            name='Cluster {}'.format(i),
            coords=[(c[0], c[1])]
        )

    kml.save('{}_{}.kml'.format('clusters', name))


def get_country_from_name(name):
    for country in COUNTRIES:
        if name in country['name']:
            return country
    return None


topics = []
topics_per_country = []
if pickle_exists(STATUSES_PICKLE_FILE):
    topics = load_pickle(TOPICS_PICKLE_FILE)
    topics_per_country = load_pickle(STATUSES_PICKLE_FILE)
else:
    topics = []
    for country in COUNTRIES:
        topics_for_location = get_top_50_trending_topics(country['id'])
        topics.append({'country': country, 'topics': topics_for_location})

    save_pickle(TOPICS_PICKLE_FILE, topics)

    for topic_for_location in topics:
        geo_result = TWITTER_API.geo.search(query=topic_for_location['country']['name'], granularity='country')
        country = list(filter(lambda result: topic_for_location['country']['name'] in result['name'],
                              geo_result['result']['places']))[0]
        country_coordinates = {
            'longitude': country['centroid'][0],
            'latitude': country['centroid'][1],
            'radius': int(math.sqrt(topic_for_location['country']['area']) / 2)
        }

        for query_index in range(TOPIC_AMOUNT_PER_COUNTRY):
            statuses_of_query = search_statuses_with_geocode_by_query(
                topic_for_location['topics'][query_index],
                country_coordinates)
            topics_per_country.append({
                'country': topic_for_location['country']['name'],
                'topic': topic_for_location['topics'][query_index],
                'statuses': statuses_of_query
            })

    save_pickle(STATUSES_PICKLE_FILE, topics_per_country)

coordinates_per_country_per_topic = []
if pickle_exists(COORDINATES_PICKLE_FILE):
    coordinates_per_country_per_topic = load_pickle(COORDINATES_PICKLE_FILE)
else:
    for topic in topics_per_country:
        coordinates_per_topic = []
        country = get_country_from_name(topic['country'])

        if country is None:
            continue

        geo_result = TWITTER_API.geo.search(query=country['name'], granularity='country')
        found_country = list(filter(lambda result: country['name'] in result['name'],
                                    geo_result['result']['places']))[0]

        country_coordinates = {
            'longitude': found_country['centroid'][0],
            'latitude': found_country['centroid'][1]
        }

        for status in topic['statuses']:
            coordinates_of_topic = get_coordinates(status, country_coordinates)
            if coordinates_of_topic is not None:
                coordinates_per_topic.append({
                    'status': status,
                    'coordinates': coordinates_of_topic,
                })

        coordinates_per_country_per_topic.append({
            'country': topic['country'],
            'topic': topic['topic'],
            'statuses': coordinates_per_topic,
        })
    save_pickle(COORDINATES_PICKLE_FILE, coordinates_per_country_per_topic)

# all countries
all_coordinates = []
for country in COUNTRIES:
    all_coordinates.extend(
        get_coordinates_from_coordinates_per_topic_for_country(coordinates_per_country_per_topic, country['name']))

save_all_coordinates(all_coordinates, 'all_countries')
save_kmeans_coordinates(all_coordinates, 'all_countries', K_ALL)

# specific countries
for country in COUNTRIES:
    save_all_coordinates(
        get_coordinates_from_coordinates_per_topic_for_country(coordinates_per_country_per_topic, country['name']),
        country['name'])
    save_kmeans_coordinates(
        get_coordinates_from_coordinates_per_topic_for_country(coordinates_per_country_per_topic, country['name']),
        country['name'], country['k'])
