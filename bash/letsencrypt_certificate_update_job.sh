#!/bin/bash

# USED IN PAIR WITH NGINX

two_and_half_months=6480000 # 86400 x 75

DOMAIN_NAME=example.com

now=$(date +'%s')
when_certificate_created=`date -d$(ls -l --time-style=long-iso /etc/letsencrypt/live | grep ${DOMAIN_NAME} | awk '{print$6}') +'%s'`
let "delta = $now - $when_certificate_created";

if [ $delta -gt $two_and_half_months ] ; then
  /usr/bin/certbot renew --no-self-upgrade
  # use [docker exec WEB_CONTAINER nginx -s reload] to reload nginx inside container
  /usr/sbin/nginx -s reload
else
  echo "Certificate already renewed at "$(date -d@$when_certificate_created +'%Y/%m/%d')
fi
