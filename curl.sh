curl --data {"user": "test", "type": "dir"} http://localhost:8080/files/test/a/blah.txt -H Content-Type: application/json
curl http://localhost:8080/files/test/a/aaaa?user=teast
curl -F user=test -F type=file -F file=@curl.sh http://localhost:8080/files/test/a/blah.txt
curl -F user=taest -F type=file -F file=@curl.sh http://localhost:8080/files/test/a/blah.txt
