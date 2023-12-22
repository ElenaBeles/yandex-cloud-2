import glob

import boto3
import configparser
import os
from pathlib import Path

from botocore.exceptions import ClientError
from bs4 import BeautifulSoup

endpoint_url = 'https://storage.yandexcloud.net'
default_region = 'ru-central1'


## фун-ции для инициализации
def init(access_key_id, secret_access_key, bucket_name):
    config = configparser.ConfigParser()

    user_config_dir = os.path.expanduser("~") + "/.config/cloudphoto"
    user_config = user_config_dir + "/cloudphotorc.ini"

    config['DEFAULT'] = {
        'aws_access_key_id': access_key_id,
        'aws_secret_access_key': secret_access_key,
        'bucket': bucket_name,
        'region': default_region,
        'endpoint_url': endpoint_url
    }

    check_and_create_bucket(bucket_name, secret_access_key, access_key_id)

    with open(user_config, 'w') as configfile:
        config.write(configfile)


def check_and_create_bucket(bucket_name, secret_access_key, access_key_id):
    session = boto3.session.Session()

    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            # Бакет не существует, создаем его
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket {bucket_name} successfully created")
            exit(0)
        else:
            print(f"Error when rotating the bucket: {e}")
            exit(1)


def init_session():
    user_config_dir = os.path.expanduser("~") + "/.config/cloudphoto"
    user_config = user_config_dir + "/cloudphotorc.ini"

    config = configparser.ConfigParser()
    config.read(user_config)

    aws_access_key_id = config['DEFAULT']['aws_access_key_id']
    aws_secret_access_key = config['DEFAULT']['aws_secret_access_key']
    endpoint_url = config['DEFAULT']['endpoint_url']
    region = config['DEFAULT']['region']
    bucket = config['DEFAULT']['bucket']

    YOS_ENDPOINT = endpoint_url
    s3BucketName = bucket

    uploader_session = boto3.session.Session(
        profile_name='uploader',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    uploader_resource = uploader_session.resource(service_name='s3', endpoint_url=YOS_ENDPOINT)
    uploader_pub_bucket = uploader_resource.Bucket(s3BucketName)

    return {
        'uploader_session': uploader_session,
        'uploader_resource': uploader_resource,
        'uploader_pub_bucket': uploader_pub_bucket,
        'YOS_ENDPOINT': YOS_ENDPOINT,
        's3BucketName': s3BucketName,
        'region': region
    }


def get_settings():
    user_config_dir = os.path.expanduser("~") + "/.config/cloudphoto"
    user_config = user_config_dir + "/cloudphotorc.ini"

    config = configparser.ConfigParser()
    config.read(user_config)

    aws_access_key_id = config['DEFAULT']['aws_access_key_id']
    aws_secret_access_key = config['DEFAULT']['aws_secret_access_key']
    endpoint_url = config['DEFAULT']['endpoint_url']
    region = config['DEFAULT']['region']
    bucket = config['DEFAULT']['bucket']

    return {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'region': region,
        'bucket': bucket
    }


## получение списка альбомов
def list_folders():
    config = init_session()

    bucket = config['uploader_pub_bucket']

    folders = set()

    for obj in bucket.objects.all():
        prefix, delimiter, _ = obj.key.rpartition('/')
        if prefix:
            folders.add(prefix)

    for folder in sorted(folders):
        print(folder)

    if len(folders) != 0:
        exit(0)

    if len(folders) == 0:
        print('Photo albums not found')
        exit(1)


## получение списка альбомов
def list_files(album):
    settings = get_settings()

    s3 = boto3.client('s3',
                      endpoint_url='https://storage.yandexcloud.net',
                      aws_access_key_id=settings['aws_access_key_id'],
                      aws_secret_access_key=settings['aws_secret_access_key']
                      )

    response = s3.list_objects_v2(Bucket=settings['bucket'], Prefix=album)
    if 'Contents' in response:
        for obj in response['Contents']:

            if obj['Key'].endswith('/'):
                continue  # Skip directories

            print(obj['Key'])
    else:
        print("There is no such album")
        exit(1)


# отправка фотографий
def upload(album, photo_dir):
    config = init_session()
    bucket = config['uploader_pub_bucket']

    file_names = []

    if not os.path.isdir(photo_dir):
        print('Warning: No such directory ' + photo_dir)
        exit(1)

    for path in os.listdir(photo_dir):
        if os.path.isfile(os.path.join(photo_dir, path)) & ((".jpg" in path) | (".jpeg" in path)):
            file_names.append(path)

    if len(file_names) == 0:
        print('Warning: Photos not found in directory ' + photo_dir)
        exit(1)

    for file_name in file_names:
        try:
            uploader_object = bucket.Object(album + '/' + file_name)
            uploader_object.upload_file(photo_dir + '/' + file_name)

        except Exception as e:
            print('Warning: Photo not sent ' + file_name)
            pass

    exit(0)


# загрузка фотографий
def download(album, photo_dir):
    try:
        settings = get_settings()

        s3 = boto3.client(
            's3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=settings['aws_access_key_id'],
            aws_secret_access_key=settings['aws_secret_access_key'],
        )

        response = s3.list_objects_v2(Bucket=settings['bucket'], Prefix=album)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']

                if key.endswith('/'):
                    continue  # Skip directories

                local_file_path = os.path.join(photo_dir, key)
                s3.download_file(settings['bucket'], key, local_file_path)

        exit(0)

    except Exception as e:
        exit(1)
        pass


## удаления альбома с фотографиями
def delete(album):
    config = init_session()
    bucket = config['uploader_pub_bucket']

    keys = []
    for file in bucket.objects.filter(Prefix=album + '/'):
        keys.append(file.key)

    if len(keys) == 0:
        print('Warning: Photo album not found ' + album)
        exit(1)

    for key in keys:
        bucket.delete_objects(Delete={
            'Objects': [
                {
                    'Key': key
                }
            ]
        })

    exit(0)

def remove_jpeg_or_jpg_suffix(input_string):
    if input_string.lower().endswith('jpeg'):
        return input_string[:-4]
    elif input_string.lower().endswith('jpg'):
        return input_string[:-3]
    else:
        return input_string


## удаление конкретной фотографии
def delete_photo(album, photo_name):
    config = init_session()
    bucket = config['uploader_pub_bucket']

    keys = []
    for file in bucket.objects.filter(Prefix=album + '/'):
        keys.append(file.key)

    if len(keys) == 0:
        print('Warning: Photo album not found ' + album)
        exit(1)

    keys_filtered = list(filter(lambda x: x.endswith(remove_jpeg_or_jpg_suffix(album + '/' + photo_name)), keys))

    if len(keys_filtered) == 0:
        print('Warning: Photo not found ' + album)
        exit(1)

    try:
        bucket.delete_objects(Delete={
            'Objects': [
                {
                    'Key': keys_filtered[0]
                }
            ]
        })

        exit(0)

    except Exception as e:
        exit(1)


## создание сайта с альбомами и фотографиями
def mksite():
    settings = get_settings()
    config = init_session()
    bucket = config['uploader_pub_bucket']

    s3 = boto3.client('s3',
                      endpoint_url='https://storage.yandexcloud.net',
                      aws_access_key_id=settings['aws_access_key_id'],
                      aws_secret_access_key=settings['aws_secret_access_key']
                      )

    s3.put_bucket_acl(
        Bucket=settings['bucket'],
        ACL='public-read'
    )

    folders = set()

    for obj in bucket.objects.all():
        prefix, delimiter, _ = obj.key.rpartition('/')
        if prefix:
            folders.add(prefix)

    folders = sorted(folders)
    bucket_website = bucket.Website()

    bucket_website.put(WebsiteConfiguration={
        "IndexDocument": {
            "Suffix": "index.html"
        },
        "ErrorDocument": {
            "Key": "error.html"
        },
    })

    index_page_content = Path('./templates/index.html').read_text(encoding='utf-8')
    soup = BeautifulSoup(index_page_content, 'html.parser')
    i = 0

    for folder in folders:
        i = i + 1
        tag = soup.new_tag("a", href='album' + str(i) + '.html')
        tag.string = 'альбом ' + folder
        soup.ul.append(tag)
        tag.wrap(soup.new_tag("li"))

    html_object = bucket.Object('index.html')
    html_object.put(Body=str(soup), ContentType='text/html')

    i = 0
    for folder in folders:
        i = i + 1

        album_page_content = Path('./templates/album-page.html').read_text(encoding='utf-8')
        soup_page = BeautifulSoup(album_page_content, 'html.parser')

        for file in bucket.objects.filter(Prefix=folder):
            tag = soup_page.new_tag("img", src=file.key, attrs={'data-title': file.key})
            soup_page.div.append(tag)

            html_object = bucket.Object('album' + str(i) + '.html')
            html_object.put(Body=str(soup_page), ContentType='text/html')

    print(f'https://{config["s3BucketName"]}.website.yandexcloud.net/index.html')
    exit(0)
