#!/bin/bash

wait-for-it.sh -t 0 mysql:3306 --strict -- /docato/src/manage.py migrate

/docato/src/manage.py ensure_admin
/docato/src/manage.py collectstatic --noinput

chmod -R a+wrx /docato_data/media/

exec $@
