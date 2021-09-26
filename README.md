# Diplom

Upload to s3:

curl -s -X POST -H "Content-Type: multipart/form-data" -F "file=@images/2227.jpg" -F "name=1" http://192.168.245.128:5000/


Download from s3

curl -s -X GET -H "Content-Type: multipart/form-data" -F "name=1" http://192.168.245.128:5000/

Upload multiple files to s3

curl -X POST -F "file=@to_upload/2.jpg" -F "file=@to_upload/3.jpg"  http://192.168.245.128:5000/upload-multiple-files

Delete Pictures

curl -s -X POST -F "name=3" http://192.168.245.128:5000/delete
curl -s -X POST http://192.168.245.128:5000/delete
