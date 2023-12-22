import argparse

from functions import init, upload, delete, mksite, list_folders, download, list_files, delete_photo

parser = argparse.ArgumentParser(prog='cloudphoto')
command_parser = parser.add_subparsers(title='command', dest='command')

command_init = command_parser.add_parser('init', help='init connection')

## 2.3. Просмотр списка альбомов и фотографий в альбоме
command_list = command_parser.add_parser('list', help='list photo albums')
command_list.add_argument('--album', dest='album', type=str, help='Photo album name', required=False)

## 2.1 Отправка фотографий в облачное хранилище
command_upload = command_parser.add_parser('upload', help='upload photos')
command_upload.add_argument('--album', dest='album', type=str, help='Photo album name', required=True)
command_upload.add_argument('--path', dest='photo_dir', type=str, default='.', help='Path to photos', required=False)

## 2.2 Загрузка фотографий из облачного хранилища
command_upload = command_parser.add_parser('download', help='download photos')
command_upload.add_argument('--album', dest='album', type=str, help='Photo album name', required=True)
command_upload.add_argument('--path', dest='photo_dir', type=str, default='.', help='Path to photos', required=False)

## 2.4. Удаление альбомов и фотографий
command_delete = command_parser.add_parser('delete', help='delete album')
command_delete.add_argument('--album', metavar='ALBUM', type=str, help='Photo album name')
command_delete.add_argument('--photo', dest='photo', type=str, help='Photo name', required=False)

## 2.5. Генерация и публикация веб-страниц фотоархива
command_mksite = command_parser.add_parser('mksite', help='start website')

args = parser.parse_args()

if args.command == 'init':
    aws_access_key_id = input('aws_access_key_id is ')
    aws_secret_access_key = input('aws_secret_access_key is ')
    bucket = input('bucket is ')

    init(aws_access_key_id, aws_secret_access_key, bucket)

elif args.command == 'list':
    if args.album:
        list_files(args.album)
    else:
        list_folders()

elif args.command == 'upload':
    upload(args.album, args.photo_dir)

elif args.command == 'download':
    download(args.album, args.photo_dir)

elif args.command == 'delete':
    if args.photo:
        delete_photo(args.album, args.photo)
    else:
        delete(args.album)

elif args.command == 'mksite':
    mksite()
